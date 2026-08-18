import React, { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle2, ChevronRight } from 'lucide-react'
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
  const [paymentMode, setPaymentMode] = useState<'upi' | 'cash'>('upi')
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
      if (!paymentMode || (paymentMode !== 'upi' && paymentMode !== 'cash')) {
        errors.paymentMode = 'Payment mode is required for ' + year + '.'
      }
      if (paymentMode === 'upi') {
        if (!paymentReference.trim()) errors.paymentReference = 'Payment reference is required for UPI payments.'
        if (!paymentProofFile) errors.paymentProof = 'Payment proof is required for UPI payments.'
      }
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

      if (year === 'Second Year' || year === 'Third Year') {
        formData.append('payment_mode', paymentMode)
      }

      if (paymentMode === 'upi') {
        if (paymentReference) {
          formData.append('payment_reference', paymentReference.trim())
        }
        if (paymentProofFile) {
          formData.append('payment_proof', paymentProofFile)
        }
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
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="overflow-hidden rounded-3xl border border-[#CC9E4C]/20 bg-gradient-to-br from-[#6B2717]/30 to-[#6B2717]/10 p-8 sm:p-12 backdrop-blur-xl shadow-2xl shadow-[#442C1B]/60"
    >
      {!submitted ? (
        <div className="space-y-8">
          {/* Form Header */}
          <div>
            <h2 className="text-2xl sm:text-3xl font-black text-[#E0D0B6] tracking-tight">
              Complete Your Registration
            </h2>
            <p className="mt-3 text-[#D4C5AC]">
              Fill out all required information to secure your spot. All fields are mandatory.
            </p>
          </div>

          {/* Personal Details Section */}
          <section className="space-y-6">
            <div>
              <p className="text-xs uppercase tracking-[0.32em] text-[#CC9E4C]/80 font-semibold">Step 1</p>
              <h3 className="mt-2 text-lg font-bold text-[#E0D0B6]">Personal Details</h3>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#E0D0B6]">First Name *</span>
                <input
                  value={firstName}
                  onChange={(e) => {
                    setFirstName(e.target.value)
                    if (validationErrors.firstName) setValidationErrors((c) => ({ ...c, firstName: '' }))
                  }}
                  className="rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/20 px-4 py-3 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] focus:bg-[#6B2717]/30 placeholder:text-[#8B9EA5]"
                  placeholder="Your first name"
                  aria-invalid={!!validationErrors.firstName}
                />
                {validationErrors.firstName && <p className="text-xs text-rose-300">{validationErrors.firstName}</p>}
              </label>

              <label className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#E0D0B6]">Last Name *</span>
                <input
                  value={lastName}
                  onChange={(e) => {
                    setLastName(e.target.value)
                    if (validationErrors.lastName) setValidationErrors((c) => ({ ...c, lastName: '' }))
                  }}
                  className="rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/20 px-4 py-3 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] focus:bg-[#6B2717]/30 placeholder:text-[#8B9EA5]"
                  placeholder="Your last name"
                  aria-invalid={!!validationErrors.lastName}
                />
                {validationErrors.lastName && <p className="text-xs text-rose-300">{validationErrors.lastName}</p>}
              </label>
            </div>

            <label className="flex flex-col gap-2">
              <span className="text-sm font-semibold text-[#E0D0B6]">Gender *</span>
              <select
                value={gender}
                onChange={(e) => {
                  setGender(e.target.value)
                  if (validationErrors.gender) setValidationErrors((c) => ({ ...c, gender: '' }))
                }}
                className="rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/20 px-4 py-3 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] focus:bg-[#6B2717]/30"
              >
                <option>Male</option>
                <option>Female</option>
                <option>Other</option>
              </select>
              {validationErrors.gender && <p className="text-xs text-rose-300">{validationErrors.gender}</p>}
            </label>
          </section>

          {/* Academic Details Section */}
          <section className="space-y-6 border-t border-[#CC9E4C]/20 pt-8">
            <div>
              <p className="text-xs uppercase tracking-[0.32em] text-[#CC9E4C]/80 font-semibold">Step 2</p>
              <h3 className="mt-2 text-lg font-bold text-[#E0D0B6]">Academic Details</h3>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#E0D0B6]">Department *</span>
                <select
                  value={department}
                  onChange={(e) => {
                    setDepartment(e.target.value)
                    if (validationErrors.department) setValidationErrors((c) => ({ ...c, department: '' }))
                  }}
                  className="rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/20 px-4 py-3 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] focus:bg-[#6B2717]/30"
                >
                  <option>Cybersecurity and Digital Forensics</option>
                  <option>Data Science and Data Analysis</option>
                  <option>Artificial Intelligence and Machine Learning</option>
                </select>
                {validationErrors.department && <p className="text-xs text-rose-300">{validationErrors.department}</p>}
              </label>

              <label className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#E0D0B6]">Academic Year *</span>
                <select
                  value={year}
                  onChange={(e) => {
                    setYear(e.target.value)
                    if (validationErrors.year) setValidationErrors((c) => ({ ...c, year: '' }))
                  }}
                  className="rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/20 px-4 py-3 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] focus:bg-[#6B2717]/30"
                >
                  <option>First Year</option>
                  <option>Second Year</option>
                  <option>Third Year</option>
                </select>
                {validationErrors.year && <p className="text-xs text-rose-300">{validationErrors.year}</p>}
              </label>
            </div>

            <div className="space-y-3">
              <p className="text-sm font-semibold text-[#E0D0B6]">Roll Number *</p>
              <div className="grid gap-3 sm:grid-cols-[140px_1fr]">
                <div className="rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/20 px-4 py-3 flex items-center">
                  <p className="text-sm font-mono font-semibold text-[#CC9E4C]">{rollPrefix}</p>
                </div>
                <input
                  value={rollSuffix}
                  onChange={(e) => {
                    setRollSuffix(e.target.value.replace(/[^0-9]/g, ''))
                    if (validationErrors.rollNumber) setValidationErrors((c) => ({ ...c, rollNumber: '' }))
                  }}
                  placeholder="e.g., 001"
                  className="rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/20 px-4 py-3 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] focus:bg-[#6B2717]/30 placeholder:text-[#8B9EA5]"
                />
              </div>
              <div className="rounded-2xl border border-[#CC9E4C]/30 bg-[#CC9E4C]/10 px-4 py-3">
                <p className="text-sm text-[#E0D0B6]">Full Roll Number: <span className="font-mono font-semibold">{fullRollNumber || `${rollPrefix}...`}</span></p>
              </div>
              {validationErrors.rollNumber && <p className="text-xs text-rose-300">{validationErrors.rollNumber}</p>}
            </div>
          </section>

          {/* Contact Details Section */}
          <section className="space-y-6 border-t border-[#CC9E4C]/20 pt-8">
            <div>
              <p className="text-xs uppercase tracking-[0.32em] text-[#CC9E4C]/80 font-semibold">Step 3</p>
              <h3 className="mt-2 text-lg font-bold text-[#E0D0B6]">Contact Details</h3>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#E0D0B6]">Phone Number *</span>
                <input
                  value={contactNumber}
                  onChange={(e) => {
                    setContactNumber(e.target.value)
                    if (validationErrors.phone) setValidationErrors((c) => ({ ...c, phone: '' }))
                  }}
                  type="tel"
                  className="rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/20 px-4 py-3 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] focus:bg-[#6B2717]/30 placeholder:text-[#8B9EA5]"
                  placeholder="10-digit number"
                  aria-invalid={!!validationErrors.phone}
                />
                {validationErrors.phone && <p className="text-xs text-rose-300">{validationErrors.phone}</p>}
              </label>

              <label className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#E0D0B6]">Email Address *</span>
                <input
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value)
                    if (validationErrors.email) setValidationErrors((c) => ({ ...c, email: '' }))
                  }}
                  type="email"
                  className="rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/20 px-4 py-3 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] focus:bg-[#6B2717]/30 placeholder:text-[#8B9EA5]"
                  placeholder="your@email.com"
                  aria-invalid={!!validationErrors.email}
                />
                {validationErrors.email && <p className="text-xs text-rose-300">{validationErrors.email}</p>}
              </label>
            </div>
          </section>

          {/* Payment Section */}
          {(year === 'Second Year' || year === 'Third Year') && (
            <section className="space-y-6 border-t border-[#CC9E4C]/20 pt-8">
              <div>
                <p className="text-xs uppercase tracking-[0.32em] text-[#CC9E4C]/80 font-semibold">Step 4</p>
                <h3 className="mt-2 text-lg font-bold text-[#E0D0B6]">Payment Information</h3>
              </div>

              <p className="text-sm text-[#D4C5AC]">
                As a {year} student, a <span className="font-semibold text-[#CC9E4C]">₹250</span> registration fee is required. Choose your preferred payment method below.
              </p>

              <label className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#E0D0B6]">Payment Mode *</span>
                <select
                  value={paymentMode}
                  onChange={(e) => {
                    const nextMode = e.target.value as 'upi' | 'cash'
                    setPaymentMode(nextMode)
                    if (nextMode === 'cash') {
                      setPaymentReference('')
                      setPaymentProofFile(null)
                    }
                    if (validationErrors.paymentMode) setValidationErrors((c) => ({ ...c, paymentMode: '' }))
                    if (validationErrors.paymentReference) setValidationErrors((c) => ({ ...c, paymentReference: '' }))
                    if (validationErrors.paymentProof) setValidationErrors((c) => ({ ...c, paymentProof: '' }))
                  }}
                  className="rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/20 px-4 py-3 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] focus:bg-[#6B2717]/30"
                >
                  <option value="upi">UPI Payment</option>
                  <option value="cash">Cash Payment</option>
                </select>
                {validationErrors.paymentMode && <p className="text-xs text-rose-300">{validationErrors.paymentMode}</p>}
              </label>

              {paymentMode === 'upi' && (
                <div className="space-y-6 rounded-2xl border border-[#CC9E4C]/30 bg-[#CC9E4C]/5 p-6">
                  <div className="space-y-4">
                    <p className="text-sm font-semibold text-[#E0D0B6]">UPI Payment Instructions:</p>
                    <div className="rounded-2xl border border-[#E0D0B6]/30 bg-[#E0D0B6]/5 p-6">
                      <img
                        src="/payment-qr.jpeg"
                        alt="Payment QR Code"
                        className="mx-auto h-56 w-56 rounded-xl border border-[#E0D0B6]/20"
                      />
                      <p className="mt-4 text-center text-sm text-[#D4C5AC]">
                        Scan this QR code with your UPI app and pay ₹250. Keep your transaction reference for verification.
                      </p>
                    </div>
                  </div>

                  <label className="flex flex-col gap-2">
                    <span className="text-sm font-semibold text-[#E0D0B6]">Transaction Reference *</span>
                    <input
                      value={paymentReference}
                      onChange={(e) => {
                        setPaymentReference(e.target.value)
                        if (validationErrors.paymentReference) setValidationErrors((c) => ({ ...c, paymentReference: '' }))
                      }}
                      placeholder="e.g., UPI/TXN/123456789 or any transaction ID"
                      className="rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/20 px-4 py-3 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] focus:bg-[#6B2717]/30 placeholder:text-[#8B9EA5]"
                    />
                    {validationErrors.paymentReference && <p className="text-xs text-[#E09999]">{validationErrors.paymentReference}</p>}
                  </label>

                  <label className="flex flex-col gap-2">
                    <span className="text-sm font-semibold text-[#E0D0B6]">Upload Payment Proof *</span>
                    <p className="text-xs text-[#8B9EA5]">Accepted: JPEG, PNG, PDF (Max 5MB)</p>
                    <input
                      type="file"
                      onChange={(e) => {
                        const file = e.target.files?.[0]
                        if (file) {
                          if (file.size > 5 * 1024 * 1024) {
                            setValidationErrors((c) => ({ ...c, paymentProof: 'File size must not exceed 5 MB.' }))
                            return
                          }
                          const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf']
                          if (!allowedTypes.includes(file.type)) {
                            setValidationErrors((c) => ({ ...c, paymentProof: 'Only JPEG, PNG, or PDF files are allowed.' }))
                            return
                          }
                          setPaymentProofFile(file)
                          if (validationErrors.paymentProof) setValidationErrors((c) => ({ ...c, paymentProof: '' }))
                        }
                      }}
                      accept=".jpg,.jpeg,.png,.pdf"
                      className="rounded-2xl border-2 border-dashed border-[#CC9E4C]/30 bg-[#CC9E4C]/5 px-4 py-4 text-[#8B9EA5] outline-none transition focus:border-[#CC9E4C] file:rounded-lg file:border-0 file:bg-[#CC9E4C]/20 file:px-3 file:py-1 file:text-sm file:font-semibold file:text-[#CC9E4C] hover:file:bg-[#CC9E4C]/30"
                    />
                    {validationErrors.paymentProof && <p className="text-xs text-[#E09999]">{validationErrors.paymentProof}</p>}
                    {paymentProofFile && (
                      <p className="text-xs text-[#CC9E4C] flex items-center gap-2">
                        <CheckCircle2 size={14} /> File selected: {paymentProofFile.name}
                      </p>
                    )}
                  </label>
                </div>
              )}

              {paymentMode === 'cash' && (
                <div className="rounded-2xl border border-[#CC9E4C]/30 bg-[#CC9E4C]/10 p-6">
                  <p className="text-sm text-[#D4C5AC]">
                    <span className="font-semibold text-[#E0D0B6]">Cash Payment Selected.</span> You'll be able to pay ₹250 in cash at the registration desk during the event. No online payment required.
                  </p>
                </div>
              )}
            </section>
          )}

          {/* Form Actions */}
          <div className="flex flex-col gap-3 pt-4 border-t border-[#CC9E4C]/20">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="button"
              onClick={submitRegistration}
              disabled={isSubmitting}
              className="w-full rounded-2xl bg-[#CC9E4C] px-6 py-4 font-semibold text-[#442C1B] shadow-lg shadow-[#CC9E4C]/40 transition hover:shadow-xl hover:shadow-[#CC9E4C]/60 hover:bg-[#6B2717] hover:text-[#E0D0B6] disabled:cursor-not-allowed disabled:opacity-70 disabled:shadow-none"
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-transparent border-t-[#442C1B] border-r-[#442C1B]" />
                  Submitting Registration...
                </span>
              ) : (
                'Submit Registration'
              )}
            </motion.button>
            {errorMessage && <p className="text-xs text-[#E09999] text-center">{errorMessage}</p>}
          </div>
        </div>
      ) : (
        // Success State
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-6"
        >
          <div className="flex justify-center">
            <motion.div
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 0.8 }}
              className="rounded-full bg-gradient-to-br from-[#CC9E4C]/30 to-[#6B2717]/30 p-8"
            >
              <CheckCircle2 size={48} className="text-[#CC9E4C]" />
            </motion.div>
          </div>

          <div className="space-y-3">
            <h2 className="text-3xl font-black text-[#E0D0B6] tracking-tight">Registration Successful!</h2>
            <p className="text-lg text-[#D4C5AC]">
              Your registration has been submitted successfully.
            </p>
          </div>

          <div className="rounded-2xl border border-[#CC9E4C]/30 bg-[#CC9E4C]/10 p-6 space-y-2">
            <p className="text-sm text-[#D4C5AC]">Your unique registration number is:</p>
            <p className="text-2xl font-mono font-black text-[#CC9E4C]">{registrationNumber}</p>
          </div>

          <div className="rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/30 p-6 space-y-3 text-left">
            <h3 className="font-semibold text-[#E0D0B6]">What's Next?</h3>
            <ul className="space-y-2 text-sm text-[#D4C5AC]">
              <li className="flex items-start gap-3">
                <span className="text-[#CC9E4C] font-bold mt-0.5 flex-shrink-0">✓</span>
                <span>Your registration is currently <strong className="text-[#E0D0B6]">pending admin approval</strong></span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-[#CC9E4C] font-bold mt-0.5 flex-shrink-0">✓</span>
                <span>A confirmation email will be sent to <strong className="text-[#E0D0B6]">{email}</strong> once approved</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-[#CC9E4C] font-bold mt-0.5 flex-shrink-0">✓</span>
                <span>Save your registration number for quick reference</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-[#CC9E4C] font-bold mt-0.5 flex-shrink-0">✓</span>
                <span>Watch out for your digital pass in your email inbox</span>
              </li>
            </ul>
          </div>

          {(year === 'Second Year' || year === 'Third Year') && paymentMode === 'upi' && (
            <div className="rounded-2xl border border-[#CC9E4C]/30 bg-[#CC9E4C]/10 p-6">
              <p className="text-sm text-[#E0D0B6]">
                <strong>Important:</strong> Our admin team will verify your payment proof. Please ensure the proof is clear and shows the transaction details.
              </p>
            </div>
          )}

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => window.location.href = '/'}
            className="rounded-full bg-[#CC9E4C] px-8 py-3 font-semibold text-[#442C1B] shadow-lg shadow-[#CC9E4C]/40 transition hover:shadow-xl hover:shadow-[#CC9E4C]/60 hover:bg-[#6B2717] hover:text-[#E0D0B6]"
          >
            Back to Home
          </motion.button>
        </motion.div>
      )}
    </motion.div>
  )
}
