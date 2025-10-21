import React, { useState } from 'react'
import Head from 'next/head'
import Image from 'next/image'

export default function UnderConstruction() {
  const [email, setEmail] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle')

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || isSubmitting) return

    setIsSubmitting(true)
    setSubmitStatus('idle')

    try {
      const response = await fetch('/api/construction/submit-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      })

      const data = await response.json()

      if (response.ok) {
        setSubmitStatus('success')
        setEmail('')
      } else {
        setSubmitStatus('error')
      }
    } catch (error) {
      console.error('Error submitting email:', error)
      setSubmitStatus('error')
    } finally {
      setIsSubmitting(false)
    }
  }
  return (
    <>
      <Head>
        <title>زیر ساخت - پلتفرم زیمر</title>
        <meta name="description" content="پلتفرم زیمر در حال توسعه است - زیرساخت یکپارچه اتوماسیون هوشمند" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style jsx>{`
          @keyframes shimmer {
            0% {
              transform: translateX(-100%) skewX(-12deg);
            }
            100% {
              transform: translateX(200%) skewX(-12deg);
            }
          }
          .animate-shimmer {
            animation: shimmer 3s ease-in-out infinite;
          }
        `}</style>
      </Head>
      
      <main className='w-full h-screen bg-[#7F5AF0] relative overflow-hidden'>
        {/* Background Grid Pattern */}
        <div className='absolute inset-0 opacity-20'>
          <div className='w-full h-full' style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px'
          }} />
        </div>

        {/* Logo - Top Right - Responsive */}
        <div className='absolute top-4 right-4 sm:top-6 sm:right-6 lg:top-6 lg:right-6 z-50'>
          <Image
            src='/images/logo.png'
            width={60}
            height={60}
            alt='Zimmer Logo'
            className='w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12'
          />
        </div>

        {/* Navigation Icons - Mobile */}
        <div className='absolute top-4 left-4 sm:hidden z-50 flex flex-col space-y-3'>
          <a 
            href='https://www.zimmerai.com/' 
            target='_blank' 
            rel='noopener noreferrer'
            className='w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-white/30 transition-colors'
          >
            <svg className='w-5 h-5 text-white' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
              <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' />
            </svg>
          </a>
          <a 
            href='https://www.zimmerai.com/survey' 
            target='_blank' 
            rel='noopener noreferrer'
            className='w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-white/30 transition-colors'
          >
            <svg className='w-5 h-5 text-white' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
              <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' />
            </svg>
          </a>
          <a 
            href='https://www.zimmerai.com/blog' 
            target='_blank' 
            rel='noopener noreferrer'
            className='w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-white/30 transition-colors'
          >
            <svg className='w-5 h-5 text-white' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
              <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z' />
            </svg>
          </a>
        </div>

        {/* Top Navbar - Desktop & Tablet */}
        <div className='hidden sm:flex absolute top-0 left-0 w-full h-16 bg-black/10 backdrop-blur-sm z-50 items-center justify-between px-6 lg:px-8'>
          {/* Left Side - Navigation Links */}
          <div className='flex items-center space-x-4 lg:space-x-6'>
            <a 
              href='https://www.zimmerai.com/' 
              target='_blank' 
              rel='noopener noreferrer'
              className='flex items-center space-x-2 text-white hover:text-white/80 transition-colors'
            >
              <svg className='w-5 h-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' />
              </svg>
              <span className='font-[Farhang2] text-sm lg:text-base'>خانه</span>
            </a>
            <a 
              href='https://www.zimmerai.com/survey' 
              target='_blank' 
              rel='noopener noreferrer'
              className='flex items-center space-x-2 text-white hover:text-white/80 transition-colors'
            >
              <svg className='w-5 h-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' />
              </svg>
              <span className='font-[Farhang2] text-sm lg:text-base'>مشاوره</span>
            </a>
            <a 
              href='https://www.zimmerai.com/blog' 
              target='_blank' 
              rel='noopener noreferrer'
              className='flex items-center space-x-2 text-white hover:text-white/80 transition-colors'
            >
              <svg className='w-5 h-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z' />
              </svg>
              <span className='font-[Farhang2] text-sm lg:text-base'>وبلاگ</span>
            </a>
          </div>

          {/* Right Side - Logo */}
          <div className='flex items-center'>
            <Image
              src='/images/logo.png'
              width={40}
              height={40}
              alt='Zimmer Logo'
              className='w-8 h-8 lg:w-10 lg:h-10'
            />
          </div>
        </div>

        {/* Right Content Section - Responsive */}
        <div className='absolute top-0 right-0 w-full sm:w-3/4 lg:w-1/2 h-full flex flex-col justify-start pt-16 sm:pt-20 lg:pt-20 sm:justify-center px-4 sm:px-8 lg:pr-16 z-30'>
          {/* Main Headline - Responsive */}
          <h1 className='text-white font-[Farhang2] text-3xl sm:text-3xl md:text-4xl lg:text-5xl font-black leading-tight mb-4 sm:mb-6 lg:mb-8 text-center sm:text-right pr-0 sm:pr-0 lg:pr-8'>
            پلتفرم زیمر در حال<br className='hidden sm:block lg:hidden' />
            <span className='sm:hidden lg:inline'> </span>توسعه است
          </h1>
          
          {/* Description Text - Responsive */}
          <div className='text-white font-[Farhang2] text-lg sm:text-base md:text-lg lg:text-xl leading-relaxed mb-6 sm:mb-8 lg:mb-12 text-center sm:text-right space-y-2 sm:space-y-3 lg:space-y-4'>
            <p>
              زیمر، زیرساخت یکپارچه اتوماسیون هوشمند برای کسب و کارهاست.
            </p>
            <p>
              از چت بات تا مدیریت فروش و داده، همه در یک پلتفرم.
            </p>
          </div>

          {/* Email Signup Form - Responsive */}
          <div className='relative bg-white/10 backdrop-blur-md rounded-2xl sm:rounded-3xl p-4 sm:p-6 lg:p-8 max-w-xs sm:max-w-sm lg:max-w-xl mx-auto sm:mx-0 sm:ml-auto border border-white/20 shadow-2xl overflow-hidden hover:border-white/40 hover:shadow-[0_0_30px_rgba(255,255,255,0.3)] transition-all duration-300'>
            {/* Animated Shimmer Effect */}
            <div className='absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 animate-shimmer'></div>
            
            {/* Content */}
            <div className='relative z-10'>
            <h3 className='text-white font-[Farhang2] text-xl sm:text-xl lg:text-2xl font-bold text-center mb-3 sm:mb-4 lg:mb-6'>
              به محض شروع خبرم کن!
            </h3>
            <form onSubmit={handleEmailSubmit} className='space-y-3 sm:space-y-4'>
              <input
                type='email'
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder='ایمیل خود را وارد کنید'
                className='w-full p-3 sm:p-4 border-2 border-[#7F5AF0] rounded-full text-center font-[Farhang2] text-base sm:text-base lg:text-lg focus:outline-none focus:ring-2 focus:ring-[#7F5AF0]'
                dir='ltr'
                required
              />
              <button 
                type='submit'
                disabled={isSubmitting}
                className='w-full bg-[#7F5AF0] text-white py-3 sm:py-4 rounded-full font-[Farhang2] text-base sm:text-base lg:text-lg font-bold hover:bg-[#6B46C1] transition-colors disabled:opacity-50 disabled:cursor-not-allowed'
              >
                {isSubmitting ? 'در حال ارسال...' : 'ارسال'}
              </button>
              {submitStatus === 'success' && (
                <p className='text-green-500 text-center text-sm'>ایمیل شما با موفقیت ثبت شد!</p>
              )}
              {submitStatus === 'error' && (
                <p className='text-red-500 text-center text-sm'>خطا در ثبت ایمیل. لطفاً دوباره تلاش کنید.</p>
              )}
            </form>
            </div>
          </div>
        </div>

        {/* Left Construction Illustration - Responsive */}
        <div className='absolute bottom-0 left-0 w-[80%] h-[50%] sm:top-0 sm:left-0 sm:transform-none sm:w-1/4 sm:h-full lg:w-1/2 z-10'>
          <div className='relative w-full h-full'>
            {/* Dots Pattern Background */}
            <Image
              src='/images/dots.png'
              alt='Dots Pattern'
              fill
              className='object-cover opacity-30'
            />
            
            {/* Complete Construction Scene with Greek Figure */}
            <Image
              src='/images/construction-scene-complete.png'
              alt='Construction Scene with Greek Figure'
              fill
              className='object-cover'
              style={{ filter: 'grayscale(0.8) brightness(1.1)' }}
            />
          </div>
        </div>

      </main>
    </>
  )
}
