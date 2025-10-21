import React, { useState, useEffect } from 'react'
import Head from 'next/head'
import Image from 'next/image'

interface ImagePosition {
  x: number
  y: number
  width: number
  height: number
  zIndex: number
}

export default function ImagePositioningTool() {
  const [image1Pos, setImage1Pos] = useState<ImagePosition>({
    x: 0, // ml-[0%] equivalent
    y: 0, // top: 0%
    width: 51, // w-[51%]
    height: 82, // h-[82%]
    zIndex: 42
  })

  const [image2Pos, setImage2Pos] = useState<ImagePosition>({
    x: 39, // ml-[39%] equivalent
    y: 0, // top: 0%
    width: 58, // w-[58%]
    height: 71, // h-[71%]
    zIndex: 9
  })

  const [isDragging, setIsDragging] = useState<string | null>(null)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })

  const handleMouseDown = (e: React.MouseEvent, imageId: string) => {
    setIsDragging(imageId)
    const rect = e.currentTarget.getBoundingClientRect()
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    })
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return

    const container = document.getElementById('positioning-container')
    if (!container) return

    const containerRect = container.getBoundingClientRect()
    const newX = ((e.clientX - dragOffset.x - containerRect.left) / containerRect.width) * 100
    const newY = ((e.clientY - dragOffset.y - containerRect.top) / containerRect.height) * 100

    // Clamp values to stay within bounds
    const clampedX = Math.max(0, Math.min(100 - (isDragging === 'image1' ? image1Pos.width : image2Pos.width), newX))
    const clampedY = Math.max(0, Math.min(100 - (isDragging === 'image1' ? image1Pos.height : image2Pos.height), newY))

    if (isDragging === 'image1') {
      setImage1Pos(prev => ({ ...prev, x: clampedX, y: clampedY }))
    } else {
      setImage2Pos(prev => ({ ...prev, x: clampedX, y: clampedY }))
    }
  }

  const handleMouseUp = () => {
    setIsDragging(null)
  }

  const updateSize = (imageId: string, dimension: 'width' | 'height', value: number) => {
    if (imageId === 'image1') {
      setImage1Pos(prev => ({ ...prev, [dimension]: value }))
    } else {
      setImage2Pos(prev => ({ ...prev, [dimension]: value }))
    }
  }

  const updateZIndex = (imageId: string, value: number) => {
    if (imageId === 'image1') {
      setImage1Pos(prev => ({ ...prev, zIndex: value }))
    } else {
      setImage2Pos(prev => ({ ...prev, zIndex: value }))
    }
  }

  const generateTailwindClasses = () => {
    const image1Classes = `w-[${image1Pos.width}%] h-[${image1Pos.height}%] z-${image1Pos.zIndex} ml-[${image1Pos.x}%] max-sm:hidden grayscale-75 object-contain`
    const image2Classes = `w-[${image2Pos.width}%] h-[${image2Pos.height}%] max-sm:w-full max-sm:m-0 ml-[${image2Pos.x}%] grayscale-75 max-sm:h-[60%] object-contain z-${image2Pos.zIndex}`
    
    return { image1Classes, image2Classes }
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      alert('Copied to clipboard!')
    } catch (err) {
      console.error('Failed to copy: ', err)
    }
  }

  const { image1Classes, image2Classes } = generateTailwindClasses()

  useEffect(() => {
    const handleGlobalMouseMove = (e: MouseEvent) => {
      if (!isDragging) return
      handleMouseMove(e as any)
    }

    const handleGlobalMouseUp = () => {
      setIsDragging(null)
    }

    if (isDragging) {
      document.addEventListener('mousemove', handleGlobalMouseMove)
      document.addEventListener('mouseup', handleGlobalMouseUp)
    }

    return () => {
      document.removeEventListener('mousemove', handleGlobalMouseMove)
      document.removeEventListener('mouseup', handleGlobalMouseUp)
    }
  }, [isDragging, dragOffset])

  return (
    <>
      <Head>
        <title>Image Positioning Tool - Zimmer Platform</title>
      </Head>
      
      <div className="min-h-screen bg-gray-100 p-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">Image Positioning Tool</h1>
          
          {/* Controls Panel */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Controls</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Image 1 Controls */}
              <div className="border rounded-lg p-4">
                <h3 className="font-semibold mb-3">Image 1 (Main Illustration)</h3>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium">X Position: {image1Pos.x.toFixed(1)}%</label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={image1Pos.x}
                      onChange={(e) => setImage1Pos(prev => ({ ...prev, x: Number(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Y Position: {image1Pos.y.toFixed(1)}%</label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={image1Pos.y}
                      onChange={(e) => setImage1Pos(prev => ({ ...prev, y: Number(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Width: {image1Pos.width}%</label>
                    <input
                      type="range"
                      min="10"
                      max="100"
                      value={image1Pos.width}
                      onChange={(e) => updateSize('image1', 'width', Number(e.target.value))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Height: {image1Pos.height}%</label>
                    <input
                      type="range"
                      min="10"
                      max="100"
                      value={image1Pos.height}
                      onChange={(e) => updateSize('image1', 'height', Number(e.target.value))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Z-Index: {image1Pos.zIndex}</label>
                    <input
                      type="range"
                      min="0"
                      max="50"
                      value={image1Pos.zIndex}
                      onChange={(e) => updateZIndex('image1', Number(e.target.value))}
                      className="w-full"
                    />
                  </div>
                </div>
              </div>

              {/* Image 2 Controls */}
              <div className="border rounded-lg p-4">
                <h3 className="font-semibold mb-3">Image 2 (Secondary Illustration)</h3>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium">X Position: {image2Pos.x.toFixed(1)}%</label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={image2Pos.x}
                      onChange={(e) => setImage2Pos(prev => ({ ...prev, x: Number(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Y Position: {image2Pos.y.toFixed(1)}%</label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={image2Pos.y}
                      onChange={(e) => setImage2Pos(prev => ({ ...prev, y: Number(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Width: {image2Pos.width}%</label>
                    <input
                      type="range"
                      min="10"
                      max="100"
                      value={image2Pos.width}
                      onChange={(e) => updateSize('image2', 'width', Number(e.target.value))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Height: {image2Pos.height}%</label>
                    <input
                      type="range"
                      min="10"
                      max="100"
                      value={image2Pos.height}
                      onChange={(e) => updateSize('image2', 'height', Number(e.target.value))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Z-Index: {image2Pos.zIndex}</label>
                    <input
                      type="range"
                      min="0"
                      max="50"
                      value={image2Pos.zIndex}
                      onChange={(e) => updateZIndex('image2', Number(e.target.value))}
                      className="w-full"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Preview Area */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Preview</h2>
            <div 
              id="positioning-container"
              className="relative w-full h-96 bg-[#7F5AF0] rounded-lg overflow-hidden"
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
            >
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

              {/* Logo - Top Right */}
              <div className='absolute top-4 right-4 z-50'>
                <Image
                  src='/images/logo.png'
                  width={30}
                  height={30}
                  alt='Zimmer Logo'
                  className='w-8 h-8'
                />
              </div>

              {/* Main Content - Right Side */}
              <div className='absolute top-0 right-0 w-1/2 h-full flex flex-col justify-center pr-8 z-30'>
                {/* Main Headline */}
                <h1 className='text-white font-[Farhang2] text-2xl font-black leading-tight mb-4 text-right'>
                  پلتفرم زیمر در حال<br />توسعه است
                </h1>
                
                {/* Description Text */}
                <div className='text-white font-[Farhang2] text-sm leading-relaxed mb-6 text-right space-y-2'>
                  <p>زیمر، زیرساخت یکپارچه اتوماسیون هوشمند برای کسب و کارهاست.</p>
                  <p>از چت بات تا مدیریت فروش و داده، همه در یک پلتفرم.</p>
                </div>

                {/* Email Signup Form */}
                <div className='bg-white rounded-2xl p-4 max-w-xs'>
                  <h3 className='text-[#7F5AF0] font-[Farhang2] text-lg font-bold text-center mb-3'>
                    اولین نفر باخبر شوید
                  </h3>
                  <div className='space-y-2'>
                    <input
                      type='email'
                      placeholder='ایمیل خود را وارد کنید'
                      className='w-full p-2 border-2 border-[#7F5AF0] rounded-full text-center font-[Farhang2] text-sm focus:outline-none focus:ring-2 focus:ring-[#7F5AF0]'
                      dir='ltr'
                    />
                    <button className='w-full bg-[#7F5AF0] text-white py-2 rounded-full font-[Farhang2] text-sm font-bold hover:bg-[#6B46C1] transition-colors'>
                      ثبت و ارسال
                    </button>
                  </div>
                </div>
              </div>

              {/* Left Side - Construction Elements */}
              <div className='absolute top-0 left-0 w-1/2 h-full z-10'>
                {/* Main Construction Scene */}
                <div className='relative w-full h-full'>
                  {/* Background Dots Pattern */}
                  <div className='absolute inset-0 z-5 opacity-30'>
                    <Image
                      src='/images/dots.png'
                      alt='Background Dots'
                      fill
                      className='object-cover'
                    />
                  </div>

                  {/* Draggable Images */}
                  <div
                    className="absolute cursor-move border-2 border-red-500"
                    style={{
                      left: `${image1Pos.x}%`,
                      top: `${image1Pos.y}%`,
                      width: `${image1Pos.width}%`,
                      height: `${image1Pos.height}%`,
                      zIndex: image1Pos.zIndex
                    }}
                    onMouseDown={(e) => handleMouseDown(e, 'image1')}
                  >
                        <Image
                          src="/images/construction-scene-complete.png"
                          alt="Construction Scene"
                          fill
                          className="object-contain"
                          style={{ filter: 'grayscale(0.8) brightness(1.1)' }}
                        />
                  </div>

                  <div
                    className="absolute cursor-move border-2 border-blue-500"
                    style={{
                      left: `${image2Pos.x}%`,
                      top: `${image2Pos.y}%`,
                      width: `${image2Pos.width}%`,
                      height: `${image2Pos.height}%`,
                      zIndex: image2Pos.zIndex
                    }}
                    onMouseDown={(e) => handleMouseDown(e, 'image2')}
                  >
                        <Image
                          src="/images/dots.png"
                          alt="Dots Pattern"
                          fill
                          className="object-contain"
                          style={{ filter: 'grayscale(0.8) brightness(1.1)' }}
                        />
                  </div>
                </div>
              </div>

              {/* Decorative Elements */}
              <div className='absolute bottom-0 left-0 w-full h-16 bg-gradient-to-t from-black/10 to-transparent z-40' />
              <div className='absolute top-0 left-0 w-full h-16 bg-gradient-to-b from-black/10 to-transparent z-40' />
            </div>
          </div>

          {/* Generated Code */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Generated Tailwind Classes</h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-medium">Image 1 Classes:</h3>
                  <button
                    onClick={() => copyToClipboard(image1Classes)}
                    className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                  >
                    Copy
                  </button>
                </div>
                <code className="block bg-gray-100 p-3 rounded text-sm break-all">
                  {image1Classes}
                </code>
              </div>
              <div>
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-medium">Image 2 Classes:</h3>
                  <button
                    onClick={() => copyToClipboard(image2Classes)}
                    className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                  >
                    Copy
                  </button>
                </div>
                <code className="block bg-gray-100 p-3 rounded text-sm break-all">
                  {image2Classes}
                </code>
              </div>
            </div>
            
            <div className="mt-6">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-medium">Complete Image Elements:</h3>
                <button
                  onClick={() => copyToClipboard(`<Image
  className='${image1Classes}'
  src={'/images/construction-scene-complete.png'}
  alt='Construction Scene'
  width={600}
  height={600}
/>
<Image
  className='${image2Classes}'
  src={'/images/dots.png'}
  alt='Dots Pattern'
  width={500}
  height={500}
/>`)}
                  className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600"
                >
                  Copy All
                </button>
              </div>
              <pre className="bg-gray-100 p-4 rounded text-sm overflow-x-auto">
{`<Image
  className='${image1Classes}'
  src={'/images/image1.png'}
  alt='background'
  width={600}
  height={600}
/>
<Image
  className='${image2Classes}'
  src={'/images/image2.png'}
  alt='background'
  width={500}
  height={500}
/>`}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
