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
      transition={{ duration: 0.8 }}
      className="w-full"
    >
      {!submitted ? (
        <form className="space-y-8">
          {/* Personal Details */}
          <fieldset className="space-y-5">
            <legend className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C] font-black">Step 1: Personal</legend>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#E0D0B6]">First Name</span>
                <input
                  value={firstName}
                  onChange={(e) => {
                    setFirstName(e.target.value)
                    if (validationErrors.firstName) setValidationErrors((c) => ({ ...c, firstName: '' }))
                  }}
                  className="bg-transparent border-b border-[#CC9E4C]/30 px-0 py-2 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] placeholder:text-[#8B9EA5]"
                  placeholder="Your name"
                />
                {validationErrors.firstName && <p className="text-xs text-[#E09999]">{validationErrors.firstName}</p>}
              </label>

              <label className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#E0D0B6]">Last Name</span>
                <input
                  value={lastName}
                  onChange={(e) => {
                    setLastName(e.target.value)
                    if (validationErrors.lastName) setValidationErrors((c) => ({ ...c, lastName: '' }))
                  }}
                  className="bg-transparent border-b border-[#CC9E4C]/30 px-0 py-2 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] placeholder:text-[#8B9EA5]"
                  placeholder="Your surname"
                />
                {validationErrors.lastName && <p className="text-xs text-[#E09999]">{validationErrors.lastName}</p>}
              </label>
            </div>

            <label className="flex flex-col gap-2">
              <span className="text-sm font-semibold text-[#E0D0B6]">Gender</span>
              <select
                value={gender}
                onChange={(e) => {
                  setGender(e.target.value)
                  if (validationErrors.gender) setValidationErrors((c) => ({ ...c, gender: '' }))
                }}
                className="bg-transparent border-b border-[#CC9E4C]/30 px-0 py-2 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C]"
              >
                <option value="Male" className="bg-[#442C1B]">Male</option>
                <option value="Female" className="bg-[#442C1B]">Female</option>
                <option value="Other" className="bg-[#442C1B]">Other</option>
              </select>
              {validationErrors.gender && <p className="text-xs text-[#E09999]">{validationErrors.gender}</p>}
            </label>
          </fieldset>

          {/* Academic Details */}
          <fieldset className="space-y-5 border-t border-[#CC9E4C]/20 pt-8">
            <legend className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C] font-black">Step 2: Academic</legend>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#E0D0B6]">Department</span>
                <select
                  value={department}
                  onChange={(e) => {
                    setDepartment(e.target.value)
                    if (validationErrors.department) setValidationErrors((c) => ({ ...c, department: '' }))
                  }}
                  className="bg-transparent border-b border-[#CC9E4C]/30 px-0 py-2 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C]"
                >
                  <option value="Cybersecurity and Digital Forensics" className="bg-[#442C1B]">Cybersecurity</option>
                  <option value="Data Science and Data Analysis" className="bg-[#442C1B]">Data Science</option>
                  <option value="Artificial Intelligence and Machine Learning" className="bg-[#442C1B]">AI & ML</option>
                </select>
                {validationErrors.department && <p className="text-xs text-[#E09999]">{validationErrors.department}</p>}
              </label>

              <label className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#E0D0B6]">Year</span>
                <select
                  value={year}
                  onChange={(e) => {
                    setYear(e.target.value)
                    if (validationErrors.year) setValidationErrors((c) => ({ ...c, year: '' }))
                  }}
                  className="bg-transparent border-b border-[#CC9E4C]/30 px-0 py-2 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C]"
                >
                  <option value="First Year" className="bg-[#442C1B]">First Year</option>
                  <option value="Second Year" className="bg-[#442C1B]">Second Year</option>
                  <option value="Third Year" className="bg-[#442C1B]">Third Year</option>
                </select>
                {validationErrors.year && <p className="text-xs text-[#E09999]">{validationErrors.year}</p>}
              </label>
            </div>

            <label className="flex flex-col gap-2">
              <span className="text-sm font-semibold text-[#E0D0B6]">Roll Number</span>
              <div className="flex gap-2">
                <div className="border-b border-[#CC9E4C]/30 px-0 py-2 flex-shrink-0">
                  <p className="text-sm font-mono font-bold text-[#CC9E4C]">{rollPrefix}</p>
                </div>
                <input
                  value={rollSuffix}
                  onChange={(e) => {
                    setRollSuffix(e.target.value.replace(/[^0-9]/g, ''))
                    if (validationErrors.rollNumber) setValidationErrors((c) => ({ ...c, rollNumber: '' }))
                  }}
                  placeholder="001"
                  className="flex-1 bg-transparent border-b border-[#CC9E4C]/30 px-0 py-2 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] placeholder:text-[#8B9EA5]"
                />
              </div>
              <p className="text-xs text-[#8B9EA5] mt-2">Full: <span className="text-[#E0D0B6] font-mono font-bold">{fullRollNumber || `${rollPrefix}...`}</span></p>
              {validationErrors.rollNumber && <p className="text-xs text-[#E09999]">{validationErrors.rollNumber}</p>}
            </label>
          </fieldset>

          {/* Contact Details */}
          <fieldset className="space-y-5 border-t border-[#CC9E4C]/20 pt-8">
            <legend className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C] font-black">Step 3: Contact</legend>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#E0D0B6]">Phone</span>
                <input
                  value={contactNumber}
                  onChange={(e) => {
                    setContactNumber(e.target.value)
                    if (validationErrors.phone) setValidationErrors((c) => ({ ...c, phone: '' }))
                  }}
                  type="tel"
                  className="bg-transparent border-b border-[#CC9E4C]/30 px-0 py-2 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] placeholder:text-[#8B9EA5]"
                  placeholder="10-digit"
                />
                {validationErrors.phone && <p className="text-xs text-[#E09999]">{validationErrors.phone}</p>}
              </label>

              <label className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#E0D0B6]">Email</span>
                <input
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value)
                    if (validationErrors.email) setValidationErrors((c) => ({ ...c, email: '' }))
                  }}
                  type="email"
                  className="bg-transparent border-b border-[#CC9E4C]/30 px-0 py-2 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] placeholder:text-[#8B9EA5]"
                  placeholder="your@email.com"
                />
                {validationErrors.email && <p className="text-xs text-[#E09999]">{validationErrors.email}</p>}
              </label>
            </div>
          </fieldset>

          {/* Payment Section - Conditional */}
          {(year === 'Second Year' || year === 'Third Year') && (
            <fieldset className="space-y-6 border-t border-[#CC9E4C]/20 pt-8">
              <legend className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C] font-black">Step 4: Payment</legend>

              <div className="bg-[#6B2717]/30 border border-[#CC9E4C]/20 p-4 rounded-lg">
                <p className="text-sm text-[#D4C5AC]">Registration fee: <span className="text-[#CC9E4C] font-bold text-lg">₹250</span></p>
              </div>

              <label className="flex flex-col gap-2">
                <span className="text-sm font-semibold text-[#E0D0B6]">Payment Method</span>
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
                  className="bg-transparent border-b border-[#CC9E4C]/30 px-0 py-2 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C]"
                >
                  <option value="upi" className="bg-[#442C1B]">UPI Payment</option>
                  <option value="cash" className="bg-[#442C1B]">Cash at Desk</option>
                </select>
                {validationErrors.paymentMode && <p className="text-xs text-[#E09999]">{validationErrors.paymentMode}</p>}
              </label>

              {paymentMode === 'upi' && (
                <div className="space-y-6 bg-[#1A120D]/75 border border-[#CC9E4C]/20 p-6 rounded-lg">
                  <div className="space-y-3">
                    <p className="text-xs uppercase tracking-[0.08em] text-[#8B9EA5] font-semibold">Scan QR to Pay ₹250</p>
                    <div className="bg-[#E0D0B6] p-4 rounded-lg flex items-center justify-center">
                      <img
                        src="/payment-qr.jpeg"
                        alt="Payment QR Code"
                        className="h-40 w-40"
                      />
                    </div>
                  </div>

                  <label className="flex flex-col gap-2">
                    <span className="text-sm font-semibold text-[#E0D0B6]">Transaction Reference</span>
                    <input
                      value={paymentReference}
                      onChange={(e) => {
                        setPaymentReference(e.target.value)
                        if (validationErrors.paymentReference) setValidationErrors((c) => ({ ...c, paymentReference: '' }))
                      }}
                      placeholder="TXN ID or Reference"
                      className="bg-transparent border-b border-[#CC9E4C]/30 px-0 py-2 text-[#E0D0B6] outline-none transition focus:border-[#CC9E4C] placeholder:text-[#8B9EA5]"
                    />
                    {validationErrors.paymentReference && <p className="text-xs text-[#E09999]">{validationErrors.paymentReference}</p>}
                  </label>

                  <label className="flex flex-col gap-3">
                    <span className="text-sm font-semibold text-[#E0D0B6]">Upload Proof</span>
                    <p className="text-xs text-[#8B9EA5]">JPEG, PNG, or PDF (Max 5MB)</p>
                    <input
                      type="file"
                      onChange={(e) => {
                        const file = e.target.files?.[0]
                        if (file) {
                          if (file.size > 5 * 1024 * 1024) {
                            setValidationErrors((c) => ({ ...c, paymentProof: 'Max 5 MB' }))
                            return
                          }
                          const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf']
                          if (!allowedTypes.includes(file.type)) {
                            setValidationErrors((c) => ({ ...c, paymentProof: 'JPEG, PNG, or PDF only' }))
                            return
                          }
                          setPaymentProofFile(file)
                          if (validationErrors.paymentProof) setValidationErrors((c) => ({ ...c, paymentProof: '' }))
                        }
                      }}
                      accept=".jpg,.jpeg,.png,.pdf"
                      className="text-xs text-[#8B9EA5] file:text-xs file:font-semibold file:text-[#CC9E4C] file:bg-transparent file:border file:border-[#CC9E4C]/30 file:px-3 file:py-1 file:rounded cursor-pointer"
                    />
                    {validationErrors.paymentProof && <p className="text-xs text-[#E09999]">{validationErrors.paymentProof}</p>}
                    {paymentProofFile && <p className="text-xs text-[#CC9E4C]">✓ {paymentProofFile.name}</p>}
                  </label>
                </div>
              )}

              {paymentMode === 'cash' && (
                <div className="bg-[#6B2717]/30 border border-[#CC9E4C]/20 p-4 rounded-lg">
                  <p className="text-sm text-[#D4C5AC]">
                    Pay ₹250 in cash at the registration desk. No online payment needed.
                  </p>
                </div>
              )}
            </fieldset>
          )}

          {/* Submit Button */}
          <div className="flex gap-3 pt-8 border-t border-[#CC9E4C]/20">
            <button
              type="button"
              onClick={submitRegistration}
              disabled={isSubmitting}
              className="flex-1 px-8 py-3 text-sm font-black tracking-[0.1em] text-[#442C1B] bg-[#CC9E4C] hover:bg-[#E0D0B6] transition duration-300 uppercase disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="h-3 w-3 animate-spin rounded-full border-2 border-transparent border-t-[#442C1B]" />
                  Submitting...
                </span>
              ) : (
                'Submit'
              )}
            </button>
          </div>

          {errorMessage && <p className="text-xs text-[#E09999] text-center">{errorMessage}</p>}
        </form>
      ) : (
        // Success State
        <div className="text-center space-y-8">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center justify-center"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-[#CC9E4C]/20 blur-xl rounded-full" />
              <div className="relative rounded-full bg-gradient-to-br from-[#CC9E4C]/30 to-[#6B2717]/20 p-6">
                <CheckCircle2 size={56} className="text-[#CC9E4C]" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="space-y-3"
          >
            <h2 className="text-4xl sm:text-5xl font-black text-[#E0D0B6] tracking-[-0.02em]">Registration Confirmed</h2>
            <p className="text-base text-[#D4C5AC] font-light">
              Your spot is secured. Check your email for next steps.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="bg-[#1A120D]/75 border border-[#CC9E4C]/30 p-6 rounded-lg space-y-2"
          >
            <p className="text-xs uppercase tracking-[0.1em] text-[#8B9EA5] font-semibold">Your Registration Number</p>
            <p className="text-3xl font-mono font-black text-[#CC9E4C]">{registrationNumber}</p>
            <p className="text-xs text-[#8B9EA5]">Save this for quick reference</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="bg-[#1A120D]/75 border border-[#CC9E4C]/20 p-6 rounded-lg space-y-4 text-left"
          >
            <h3 className="font-bold text-[#E0D0B6] uppercase text-xs tracking-[0.1em]">What Happens Next</h3>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start gap-3">
                <span className="text-[#CC9E4C] font-bold mt-0.5 flex-shrink-0">1</span>
                <span className="text-[#D4C5AC]">Admin verification of your registration</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-[#CC9E4C] font-bold mt-0.5 flex-shrink-0">2</span>
                <span className="text-[#D4C5AC]">Confirmation email to <span className="text-[#E0D0B6] font-semibold">{email}</span></span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-[#CC9E4C] font-bold mt-0.5 flex-shrink-0">3</span>
                <span className="text-[#D4C5AC]">Your digital pass & event details</span>
              </li>
            </ul>
          </motion.div>

          {(year === 'Second Year' || year === 'Third Year') && paymentMode === 'upi' && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="bg-[#1A120D]/80 border border-[#CC9E4C]/30 p-4 rounded-lg text-sm text-[#D4C5AC]"
            >
              <p>
                <span className="font-bold text-[#E0D0B6]">Payment Verification:</span> Our team will review your proof. You'll receive a confirmation once verified.
              </p>
            </motion.div>
          )}

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => window.location.href = '/'}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="inline-block px-12 py-3 text-sm font-black tracking-[0.15em] text-[#442C1B] bg-[#CC9E4C] hover:bg-[#E0D0B6] transition duration-300 uppercase mt-4"
          >
            Back to Home
          </motion.button>
        </div>
      )}
    </motion.div>
  )
}
