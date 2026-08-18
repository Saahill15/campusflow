from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.registration import Registration, RegistrationStatus
from repos.registration_repo import RegistrationRepository
from services.registration_number import RegistrationNumberGenerator
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from models.pass_model import Pass, PassStatus
from models.qr_code import QRCode, QRStatus
from repos.pass_repo import PassRepository
from repos.qr_repo import QRCodeRepository
import uuid
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)


class RegistrationService:
    def __init__(self, session: AsyncSession):
        self.repo = RegistrationRepository(session)
        self.session = session

    async def get(self, id: str) -> Optional[Registration]:
        return await self.repo.get_by_id(id)

    async def get_by_registration_number(self, registration_number: str) -> Optional[Registration]:
        return await self.repo.get_by_registration_number(registration_number)

    async def get_by_user_and_event(self, user_id: int, event_id: str) -> Optional[Registration]:
        return await self.repo.get_by_user_and_event(user_id, event_id)

    async def list(self, limit: int = 100, offset: int = 0):
        return await self.repo.list(limit=limit, offset=offset)

    async def create(self, reg: Registration) -> Registration:
        r = await self.repo.create(reg)
        await self.session.commit()
        return r

    async def create_registration(self, payload: dict, event_id: str) -> Registration:
        normalized_email = (payload.get('email') or '').strip().lower()
        normalized_roll = (payload.get('roll_number') or '').strip().upper()
        academic_year = (payload.get('academic_year') or '').strip()

        duplicate_statuses = [
            RegistrationStatus.Pending,
            RegistrationStatus.Approved,
            RegistrationStatus.Cancelled,
            RegistrationStatus.CheckedIn,
        ]

        if normalized_email:
            existing_email = await self.repo.get_by_event_and_email(
                event_id,
                normalized_email,
                statuses=duplicate_statuses,
            )
            if existing_email:
                raise ValueError('duplicate_email')

        if normalized_roll:
            existing_roll = await self.repo.get_by_event_and_roll_number(
                event_id,
                normalized_roll,
                statuses=duplicate_statuses,
            )
            if existing_roll:
                raise ValueError('duplicate_roll_number')

        # Validate payment requirements based on academic year
        payment_status = 'not_required'
        payment_amount = None
        payment_reference = (payload.get('payment_reference') or '').strip() or None
        payment_proof = (payload.get('payment_proof') or '').strip() or None

        if academic_year in ('Second Year', 'Third Year'):
            # Payment is required for Second and Third year students
            if not payment_reference:
                raise ValueError('Payment reference is required for Second and Third Year registrations.')
            if not payment_proof:
                raise ValueError('Payment proof is required for Second and Third Year registrations.')
            payment_status = 'pending'
            payment_amount = 250.0  # Fixed amount in INR (₹250)

        reg = Registration(
            event_id=event_id,
            user_id=None,
            first_name=(payload.get('first_name') or '').strip(),
            last_name=(payload.get('last_name') or '').strip(),
            department=(payload.get('department') or '').strip(),
            academic_year=academic_year,
            roll_number=normalized_roll,
            phone=(payload.get('phone') or '').strip(),
            email=normalized_email,
            gender=(payload.get('gender') or '').strip(),
            status=RegistrationStatus.Pending,
            payment_status=payment_status,
            payment_amount=payment_amount,
            payment_reference=payment_reference,
            payment_proof=payment_proof,
        )

        max_retries = 5
        for attempt in range(max_retries):
            reg.registration_number = await self.generate_registration_number()
            try:
                return await self.create(reg)
            except IntegrityError as exc:
                orig = getattr(exc, 'orig', None)
                message = str(orig).lower() if orig is not None else str(exc).lower()
                pgcode = getattr(orig, 'pgcode', None)
                retry_on_registration_number_conflict = (
                    pgcode == '23505'
                    and 'registration_number' in message
                ) or (
                    'registration_number' in message
                    and ('unique constraint' in message or 'unique failed' in message or 'duplicate' in message)
                )
                if retry_on_registration_number_conflict:
                    await self.session.rollback()
                    if attempt == max_retries - 1:
                        raise
                    continue
                raise

    async def update(self, reg: Registration) -> Registration:
        r = await self.repo.update(reg)
        await self.session.commit()
        return r

    async def delete(self, reg: Registration) -> None:
        await self.repo.delete(reg)
        await self.session.commit()

    async def generate_registration_number(self) -> str:
        # Generate a candidate; caller should assign and commit. This helper returns a candidate string.
        return await RegistrationNumberGenerator.generate_candidate(self.session)

    async def approve_registration(self, registration_id: str, approver_user_id: int) -> Registration:
        reg = await self.repo.get_by_id(registration_id)
        if not reg:
            raise ValueError('Registration not found')
        if reg.status != RegistrationStatus.Pending:
            raise ValueError('Only pending registrations can be approved')

        reg.status = RegistrationStatus.Approved
        reg.approved_by = approver_user_id
        reg.approved_at = datetime.now(timezone.utc)

        # Generate registration_number if missing; ensure uniqueness by retrying on IntegrityError
        if not reg.registration_number:
            max_retries = 5
            for attempt in range(max_retries):
                candidate = await RegistrationNumberGenerator.generate_candidate(self.session)
                reg.registration_number = candidate
                self.session.add(reg)
                try:
                    await self.session.flush()
                    break
                except IntegrityError:
                    await self.session.rollback()
                    # try again
                    if attempt == max_retries - 1:
                        raise

        # Create pass and QR atomically inside the same DB transaction
        pass_repo = PassRepository(self.session)
        qr_repo = QRCodeRepository(self.session)

        reg_id = reg.id
        reg_event_id = reg.event_id
        max_retries = 5
        for attempt in range(max_retries):
            try:
                logger.info(f"approve_registration: attempt {attempt+1} for registration {registration_id}")
                # Ensure registration_number exists (existing logic already handled above)
                # If a pass already exists for this registration, reuse it (idempotent)
                existing_pass = await pass_repo.get_by_registration(reg_id)
                logger.info(f"approve_registration: existing_pass={existing_pass}")
                if not existing_pass:
                    # generate a pass_number candidate similar to registration scheme
                    # find next numeric suffix using prefix PG26-P
                    prefix = 'PG26-P'
                    q = await self.session.execute(
                        select(Pass.pass_number).where(Pass.pass_number != None)
                    )
                    nums = []
                    for v in q.scalars().all():
                        try:
                            if v and v.startswith(prefix + '-'):
                                parts = v.split('-')
                                num = int(parts[-1])
                                nums.append(num)
                        except Exception:
                            continue
                    next_num = 1
                    if nums:
                        next_num = max(nums) + 1
                    pass_number_candidate = f"{prefix}-{next_num:06d}"

                    p = Pass(
                        event_id=reg_event_id,
                        registration_id=reg_id,
                        pass_number=pass_number_candidate,
                        status=PassStatus.Issued,
                        issued_at=datetime.now(timezone.utc),
                    )
                    self.session.add(p)
                    await self.session.flush()
                    created_pass = p
                    logger.info(f"approve_registration: created_pass id={created_pass.id} pass_number={created_pass.pass_number}")
                else:
                    created_pass = existing_pass

                # Ensure QR exists for the pass (idempotent)
                existing_qr = await qr_repo.get_by_pass(created_pass.id)
                if not existing_qr:
                    token = str(uuid.uuid4())
                    qr = QRCode(
                        pass_id=created_pass.id,
                        qr_token=token,
                        status=QRStatus.Pending,
                        generated_at=datetime.now(timezone.utc),
                    )
                    self.session.add(qr)
                    await self.session.flush()
                    logger.info(f"approve_registration: created_qr id={qr.id} token={qr.qr_token}")

                self.session.add(reg)
                await self.session.commit()
                logger.info(f"approve_registration: committed registration {reg_id}")
                return reg
            except IntegrityError as exc:
                await self.session.rollback()
                # retry in case of unique collisions on pass_number/qr_token
                if attempt == max_retries - 1:
                    raise ValueError('Failed to approve registration due to duplicate pass or QR generation.') from exc

    async def reject_registration(self, registration_id: str, approver_user_id: int, reason: str) -> Registration:
        if not reason or not reason.strip():
            raise ValueError('Rejected reason is required')
        reg = await self.repo.get_by_id(registration_id)
        if not reg:
            raise ValueError('Registration not found')
        if reg.status != RegistrationStatus.Pending:
            raise ValueError('Only pending registrations can be rejected')

        reg.status = RegistrationStatus.Rejected
        reg.rejected_reason = reason.strip()
        reg.approved_by = None
        reg.approved_at = None

        self.session.add(reg)
        await self.session.commit()
        return reg
