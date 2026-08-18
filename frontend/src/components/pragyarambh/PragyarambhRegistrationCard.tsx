import React, { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import api from '../../services/api/axios'

export default function PragyarambhRegistrationCard() {
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [department, setDepartment] = useState('Cybersecurity and Digital Forensics')
  const [year, setYear] = useState('First Year')
  const [rollSuffix, setRollSuffix] = useState('')
  const [contactNumber, setContactNumber] = useState('')
  const [email, setEmail] = useState('')
  const [gender, setGender] = useState('Male')
  const [paymentReference, setPaymentReference] = useState('')
  const [paymentProofFile, setPaymentProofFile] = useState<File | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [registrationNumber, setRegistrationNumber] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})

  const rollPrefix = useMemo(() => {
    const yearCode = year === 'First Year' ? '26' : year === 'Second Year' ? '25' : '24'
    const deptCode = department.includes('Cybersecurity') ? 'FCS' : department.includes('Data Science') ? 'FDA' : 'FAI'
    return `${deptCode}${yearCode}`
  }, [department, year])

  const fullRollNumber = `${rollPrefix}${rollSuffix}`

  useEffect(() => {
    setRollSuffix((current) => current.replace(/[^0-9]/g, ''))
  }, [department, year])

  const validateForm = () => {
    const errors: Record<string, string> = {}

    if (!firstName.trim()) errors.firstName = 'First name is required.'
    if (!lastName.trim()) errors.lastName = 'Last name is required.'
    if (!gender.trim()) errors.gender = 'Gender is required.'
    if (!department.trim()) errors.department = 'Department is required.'
    if (!year.trim()) errors.year = 'Academic year is required.'
    if (!fullRollNumber.trim()) errors.rollNumber = 'Full roll number is required.'

    const phoneDigits = contactNumber.replace(/\D/g, '')
    if (!phoneDigits || phoneDigits.length < 7) errors.phone = 'Please enter a valid phone number.'

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!email.trim() || !emailPattern.test(email)) errors.email = 'Please enter a valid email address.'

    // Payment validation for Second and Third Year
    if (year === 'Second Year' || year === 'Third Year') {
      if (!paymentReference.trim()) errors.paymentReference = 'Payment reference is required for ' + year + '.'
      if (!paymentProofFile) errors.paymentProof = 'Payment proof is required for ' + year + '.'
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const submitRegistration = async () => {
    setErrorMessage('')
    setSuccessMessage('')
    setRegistrationNumber('')
    setSubmitted(false)

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    try {
      // Build FormData for file upload
      const formData = new FormData()
      formData.append('first_name', firstName.trim())
      formData.append('last_name', lastName.trim())
      formData.append('department', department.trim())
      formData.append('academic_year', year.trim())
      formData.append('roll_number', fullRollNumber.trim())
      formData.append('phone', contactNumber.trim())
      formData.append('email', email.trim().toLowerCase())
      formData.append('gender', gender.trim())

      if (paymentReference) {
        formData.append('payment_reference', paymentReference.trim())
      }

      if (paymentProofFile) {
        formData.append('payment_proof', paymentProofFile)
      }

      // Submit with multipart/form-data to handle file upload
      const response = await axios.post(
        `${api.defaults.baseURL || '/api/v1'}/registration/with-proof`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 30000,
        }
      )

      if (response.status === 200) {
        setRegistrationNumber(response.data.registration_number)
        setSuccessMessage(response.data.message || 'Registration submitted successfully.')
        setSubmitted(true)
      }
    } catch (err: unknown) {
      const message = axios.isAxiosError(err) && err.response?.data?.detail
        ? String(err.response.data.detail)
        : 'We could not submit your registration right now. Please try again.'
      setErrorMessage(message)
      setSubmitted(false)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <motion.aside
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.9, ease: 'easeOut' }}
      className="overflow-hidden rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/40 backdrop-blur-xl"
    >
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.32em] text-cyan-200/90">Register now</p>
          <h3 className="mt-3 text-2xl font-bold text-white">Secure your seat</h3>
        </div>
      </div>

      <p className="mt-4 text-sm leading-6 text-slate-300">
        Fill in your details and get ready to be part of a night that feels premium, smooth and fully tailored for freshers.
      </p>

      <div className="mt-8 grid gap-6">
        <section className="rounded-3xl border border-white/10 bg-white/5 p-6">
          <div className="mb-6 flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.32em] text-cyan-200/90">Personal details</p>
              <h4 className="mt-2 text-lg font-semibold text-white">Personal Details</h4>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="flex flex-col gap-2 text-sm text-slate-100">
              <span className="flex items-center gap-1">First Name <span className="text-rose-300">*</span></span>
              <input
                value={firstName}
                onChange={(e) => {
                  setFirstName(e.target.value)
                  if (validationErrors.firstName) {
                    setValidationErrors((current) => ({ ...current, firstName: '' }))
                  }
                }}
                aria-invalid={!!validationErrors.firstName}
                aria-describedby={validationErrors.firstName ? 'first-name-error' : undefined}
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                required
              />
              {validationErrors.firstName && <p id="first-name-error" className="text-xs text-rose-300">{validationErrors.firstName}</p>}
            </label>
            <label className="flex flex-col gap-2 text-sm text-slate-100">
              <span className="flex items-center gap-1">Last Name <span className="text-rose-300">*</span></span>
              <input
                value={lastName}
                onChange={(e) => {
                  setLastName(e.target.value)
                  if (validationErrors.lastName) {
                    setValidationErrors((current) => ({ ...current, lastName: '' }))
                  }
                }}
                aria-invalid={!!validationErrors.lastName}
                aria-describedby={validationErrors.lastName ? 'last-name-error' : undefined}
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                required
              />
              {validationErrors.lastName && <p id="last-name-error" className="text-xs text-rose-300">{validationErrors.lastName}</p>}
            </label>
          </div>

          <label className="mt-4 flex flex-col gap-2 text-sm text-slate-100">
            <span className="flex items-center gap-1">Gender <span className="text-rose-300">*</span></span>
            <select
              value={gender}
              onChange={(e) => {
                setGender(e.target.value)
                if (validationErrors.gender) {
                  setValidationErrors((current) => ({ ...current, gender: '' }))
                }
              }}
              aria-invalid={!!validationErrors.gender}
              aria-describedby={validationErrors.gender ? 'gender-error' : undefined}
              className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
              required
            >
              <option>Male</option>
              <option>Female</option>
              <option>Other</option>
            </select>
            {validationErrors.gender && <p id="gender-error" className="text-xs text-rose-300">{validationErrors.gender}</p>}
          </label>
        </section>

        <section className="rounded-3xl border border-white/10 bg-white/5 p-6">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.32em] text-cyan-200/90">Academic details</p>
            <h4 className="mt-2 text-lg font-semibold text-white">Academic Details</h4>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="flex flex-col gap-2 text-sm text-slate-100">
              <span className="flex items-center gap-1">Department <span className="text-rose-300">*</span></span>
              <select
                value={department}
                onChange={(e) => {
                  setDepartment(e.target.value)
                  if (validationErrors.department) {
                    setValidationErrors((current) => ({ ...current, department: '' }))
                  }
                }}
                aria-invalid={!!validationErrors.department}
                aria-describedby={validationErrors.department ? 'department-error' : undefined}
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                required
              >
                <option>Cybersecurity and Digital Forensics</option>
                <option>Data Science and Data Analysis</option>
                <option>Artificial Intelligence and Machine Learning</option>
              </select>
              {validationErrors.department && <p id="department-error" className="text-xs text-rose-300">{validationErrors.department}</p>}
            </label>
            <label className="flex flex-col gap-2 text-sm text-slate-100">
              <span className="flex items-center gap-1">Academic Year <span className="text-rose-300">*</span></span>
              <select
                value={year}
                onChange={(e) => {
                  setYear(e.target.value)
                  if (validationErrors.year) {
                    setValidationErrors((current) => ({ ...current, year: '' }))
                  }
                }}
                aria-invalid={!!validationErrors.year}
                aria-describedby={validationErrors.year ? 'year-error' : undefined}
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                required
              >
                <option>First Year</option>
                <option>Second Year</option>
                <option>Third Year</option>
              </select>
              {validationErrors.year && <p id="year-error" className="text-xs text-rose-300">{validationErrors.year}</p>}
            </label>
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-[1fr_1.2fr]">
            <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-slate-200">
              <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/90">Prefix</p>
              <p className="mt-2 text-lg font-semibold text-white">{rollPrefix}</p>
            </div>
            <label className="flex flex-col gap-2 text-sm text-slate-100">
              <span className="flex items-center gap-1">Roll Number suffix <span className="text-rose-300">*</span></span>
              <input
                value={rollSuffix}
                onChange={(e) => {
                  setRollSuffix(e.target.value.replace(/[^0-9]/g, ''))
                  if (validationErrors.rollNumber) {
                    setValidationErrors((current) => ({ ...current, rollNumber: '' }))
                  }
                }}
                placeholder="e.g. 001"
                aria-invalid={!!validationErrors.rollNumber}
                aria-describedby={validationErrors.rollNumber ? 'roll-number-error' : undefined}
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                required
              />
              {validationErrors.rollNumber && <p id="roll-number-error" className="text-xs text-rose-300">{validationErrors.rollNumber}</p>}
            </label>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/5 p-5 text-sm text-slate-300">
            <p className="font-semibold text-white">Full roll number</p>
            <p className="mt-2 text-lg text-cyan-200">{fullRollNumber || `${rollPrefix}...`}</p>
          </div>
        </section>

        <section className="rounded-3xl border border-white/10 bg-white/5 p-6">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.32em] text-cyan-200/90">Contact details</p>
            <h4 className="mt-2 text-lg font-semibold text-white">Contact Details</h4>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="flex flex-col gap-2 text-sm text-slate-100">
              <span className="flex items-center gap-1">Phone <span className="text-rose-300">*</span></span>
              <input
                value={contactNumber}
                onChange={(e) => {
                  setContactNumber(e.target.value)
                  if (validationErrors.phone) {
                    setValidationErrors((current) => ({ ...current, phone: '' }))
                  }
                }}
                aria-invalid={!!validationErrors.phone}
                aria-describedby={validationErrors.phone ? 'phone-error' : undefined}
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                required
              />
              {validationErrors.phone && <p id="phone-error" className="text-xs text-rose-300">{validationErrors.phone}</p>}
            </label>
            <label className="flex flex-col gap-2 text-sm text-slate-100">
              <span className="flex items-center gap-1">Email <span className="text-rose-300">*</span></span>
              <input
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  if (validationErrors.email) {
                    setValidationErrors((current) => ({ ...current, email: '' }))
                  }
                }}
                type="email"
                aria-invalid={!!validationErrors.email}
                aria-describedby={validationErrors.email ? 'email-error' : undefined}
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                required
              />
              {validationErrors.email && <p id="email-error" className="text-xs text-rose-300">{validationErrors.email}</p>}
            </label>
          </div>
        </section>

        {(year === 'Second Year' || year === 'Third Year') && (
          <section className="rounded-3xl border border-white/10 bg-white/5 p-6">
            <div className="mb-6">
              <p className="text-xs uppercase tracking-[0.32em] text-cyan-200/90">Payment</p>
              <h4 className="mt-2 text-lg font-semibold text-white">Payment Details</h4>
            </div>

            <p className="mb-6 text-sm text-slate-300">
              As a {year} student, payment is required to complete your registration.
            </p>

            <div className="mb-6 rounded-2xl border border-white/10 bg-white/5 p-4">
              <img
                src="/payment-qr.jpeg"
                alt="Payment QR Code"
                className="mx-auto h-48 w-48 rounded"
              />
              <p className="mt-4 text-center text-xs text-slate-400">
                Scan the QR code or use the payment reference below to make your payment.
              </p>
            </div>

            <label className="flex flex-col gap-2 text-sm text-slate-100">
              <span className="flex items-center gap-1">Payment Reference <span className="text-rose-300">*</span></span>
              <input
                value={paymentReference}
                onChange={(e) => {
                  setPaymentReference(e.target.value)
                  if (validationErrors.paymentReference) {
                    setValidationErrors((current) => ({ ...current, paymentReference: '' }))
                  }
                }}
                placeholder="e.g., UPI/Transaction ID from payment gateway"
                aria-invalid={!!validationErrors.paymentReference}
                aria-describedby={validationErrors.paymentReference ? 'payment-reference-error' : undefined}
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                required
              />
              {validationErrors.paymentReference && (
                <p id="payment-reference-error" className="text-xs text-rose-300">{validationErrors.paymentReference}</p>
              )}
            </label>

            <label className="mt-4 flex flex-col gap-2 text-sm text-slate-100">
              <span className="flex items-center gap-1">Upload Payment Proof <span className="text-rose-300">*</span></span>
              <input
                type="file"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) {
                    if (file.size > 5 * 1024 * 1024) {
                      setValidationErrors((current) => ({
                        ...current,
                        paymentProof: 'File size must not exceed 5 MB.',
                      }))
                      return
                    }
                    const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf']
                    if (!allowedTypes.includes(file.type)) {
                      setValidationErrors((current) => ({
                        ...current,
                        paymentProof: 'Only JPEG, PNG, or PDF files are allowed.',
                      }))
                      return
                    }
                    setPaymentProofFile(file)
                    if (validationErrors.paymentProof) {
                      setValidationErrors((current) => ({ ...current, paymentProof: '' }))
                    }
                  }
                }}
                accept=".jpg,.jpeg,.png,.pdf"
                aria-invalid={!!validationErrors.paymentProof}
                aria-describedby={validationErrors.paymentProof ? 'payment-proof-error' : undefined}
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-slate-400 outline-none transition focus:border-cyan-300"
                required
              />
              {validationErrors.paymentProof && (
                <p id="payment-proof-error" className="text-xs text-rose-300">{validationErrors.paymentProof}</p>
              )}
              {paymentProofFile && (
                <p className="text-xs text-cyan-300">✓ File selected: {paymentProofFile.name}</p>
              )}
            </label>
          </section>
        )}

        <button
          type="button"
          onClick={submitRegistration}
          disabled={isSubmitting}
          className="w-full rounded-3xl bg-gradient-to-r from-cyan-500 to-indigo-600 px-6 py-4 text-lg font-semibold text-white transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isSubmitting ? 'Submitting...' : 'Submit Registration'}
        </button>
      </div>

      {errorMessage && (
        <div className="mt-6 rounded-3xl border border-rose-400/20 bg-rose-500/10 p-4 text-sm text-slate-100">
          <p className="font-semibold text-white">Registration could not be completed.</p>
          <p className="mt-1 text-slate-300">{errorMessage}</p>
        </div>
      )}

      {submitted && successMessage && (
        <div className="mt-6 rounded-3xl border border-cyan-300/20 bg-cyan-500/10 p-6 text-sm text-slate-100">
          <p className="text-lg font-semibold text-white">Registration Submitted Successfully</p>
          <p className="mt-3 text-slate-300">
            Your registration has been successfully received and is currently awaiting verification by the Pragyarambh team.
          </p>

          {registrationNumber && (
            <div className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-5 text-slate-200">
              <p className="text-sm uppercase tracking-[0.25em] text-cyan-200">Registration Number</p>
              <p className="mt-2 text-lg font-semibold text-white">{registrationNumber}</p>
            </div>
          )}

          <div className="mt-4 rounded-3xl border border-white/10 bg-white/5 p-5 text-slate-200">
            <p className="text-sm uppercase tracking-[0.25em] text-cyan-200">Status</p>
            <p className="mt-2 text-lg font-semibold text-white">Pending Approval</p>
          </div>

          <div className="mt-4 rounded-3xl border border-white/10 bg-white/5 p-5 text-slate-200">
            <p className="text-sm leading-6">
              Your registration is now pending approval. Once approved, your official Pragyarambh 2026 pass will be issued to your registered email address.
            </p>
          </div>
        </div>
      )}
    </motion.aside>
  )
}
