import { useState, useRef, useEffect } from 'react'
import Player from 'xgplayer'
import 'xgplayer/dist/index.min.css'
import './App.css'

function App() {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [parsingProgress, setParsingProgress] = useState(0)
  const [subtitles, setSubtitles] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentVideo, setCurrentVideo] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)
  const playerRef = useRef(null)
  const playerInstance = useRef(null)

  const openUploadModal = () => {
    setIsUploadModalOpen(true)
  }

  const closeUploadModal = () => {
    setIsUploadModalOpen(false)
    setUploadProgress(0)
  }

  const clearVideo = () => {
    // 销毁播放器
    if (playerInstance.current) {
      playerInstance.current.destroy()
      playerInstance.current = null
    }
    // 释放视频URL
    if (videoUrl) {
      URL.revokeObjectURL(videoUrl)
    }
    // 重置状态
    setCurrentVideo(null)
    setVideoUrl(null)
    setSubtitles([])
  }

  const downloadSubtitles = () => {
    // 将字幕转换为SRT格式
    let srtContent = ''
    subtitles.forEach((subtitle, index) => {
      srtContent += `${index + 1}\n`
      srtContent += `${subtitle.time.replace(' - ', ' --> ')}\n`
      srtContent += `${subtitle.text}\n\n`
    })
    
    // 创建下载链接
    const blob = new Blob([srtContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'subtitles.srt'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const downloadAudio = () => {
    // 这里需要调用后端API来获取音频文件
    // 暂时使用模拟实现
    alert('音频下载功能正在开发中，敬请期待！')
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    // 检查是否有正在处理的视频
    if (isProcessing) {
      alert('视频格式不正确')
      return
    }

    // 模拟文件上传进度
    setUploadProgress(0)
    let progress = 0
    const interval = setInterval(() => {
      progress += 10
      setUploadProgress(progress)
      if (progress >= 100) {
        clearInterval(interval)
        // 上传完成后开始解析
        processVideo(file)
      }
    }, 300)
  }

  const processVideo = async (file) => {
    setIsProcessing(true)
    setParsingProgress(0)
    
    try {
      // 保存当前视频并创建视频URL
      setCurrentVideo(file)
      const url = URL.createObjectURL(file)
      setVideoUrl(url)
      
      // 模拟解析进度
      let progress = 0
      const progressInterval = setInterval(() => {
        progress += 5
        setParsingProgress(progress)
        if (progress >= 95) {
          clearInterval(progressInterval)
        }
      }, 200)

      // 创建 FormData 并添加文件
      const formData = new FormData()
      formData.append('file', file)

      // 调用后端 API
      const response = await fetch('/api/process-video', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error('API 请求失败')
      }

      const result = await response.json()
      
      // 解析字幕结果
      const parsedSubtitles = parseSubtitles(result.subtitles)
      setSubtitles(parsedSubtitles)
    } catch (error) {
      console.error('处理视频失败:', error)
      // 改进错误提示
      alert(`处理视频失败: ${error.message}\n请检查视频格式是否正确，或稍后重试`)
    } finally {
      setParsingProgress(100)
      setIsProcessing(false)
    }
  }

  const parseSubtitles = (subtitleText) => {
    // 改进的字幕解析逻辑，支持完整的字幕格式
    const lines = subtitleText.split('\n')
    const subtitles = []
    
    let i = 0
    while (i < lines.length) {
      // 跳过空行
      while (i < lines.length && lines[i].trim() === '') {
        i++
      }
      
      if (i >= lines.length) break
      
      // 字幕序号
      i++
      
      // 时间线
      if (i < lines.length) {
        const timeLine = lines[i].trim()
        if (timeLine) {
          // 提取时间范围
          const timeMatch = timeLine.match(/(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})/)
          if (timeMatch) {
            const startTime = timeMatch[1].substring(0, 8) // 只保留时分秒
            const endTime = timeMatch[2].substring(0, 8) // 只保留时分秒
            const timeRange = `${startTime} - ${endTime}`
            
            // 字幕文本
            i++
            let text = ''
            while (i < lines.length && lines[i].trim() !== '') {
              text += lines[i].trim() + ' ' // 合并多行文本
              i++
            }
            
            if (text.trim()) {
              subtitles.push({
                time: timeRange,
                text: text.trim()
              })
            }
          } else {
            i++
          }
        } else {
          i++
        }
      }
    }
    
    return subtitles.length > 0 ? subtitles : [
      { time: '00:00:00 - 00:00:00', text: '解析成功，但未提取到字幕' }
    ]
  }

  // 初始化播放器
  useEffect(() => {
    if (videoUrl && playerRef.current) {
      // 销毁现有播放器
      if (playerInstance.current) {
        playerInstance.current.destroy()
      }
      
      // 创建新播放器
      playerInstance.current = new Player({
        el: playerRef.current,
        url: videoUrl,
        width: '100%',
        height: 400,
        autoplay: false,
        controls: true
      })
    }
    
    // 清理函数
    return () => {
      if (playerInstance.current) {
        playerInstance.current.destroy()
      }
      // 不要在这里释放videoUrl，因为组件可能还在使用它
    }
  }, [videoUrl])

  // 当组件卸载时释放视频URL
  useEffect(() => {
    return () => {
      if (videoUrl) {
        URL.revokeObjectURL(videoUrl)
      }
    }
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <h1>视频解析与字幕提取工具</h1>
      </header>
      
      <main className="app-main">
        {/* 操作区 */}
        <div className="operation-area">
          <div className="operation-row">
            <button 
              className="btn btn-secondary" 
              onClick={openUploadModal}
            >
              解析视频
            </button>
          </div>
          <div className="operation-row">
            <a 
              href="https://www.hellotik.app/zh/bilibili" 
              target="_blank" 
              rel="noopener noreferrer"
              className="download-link"
            >
              下载视频
            </a>
            {videoUrl && (
              <button 
                className="btn btn-clear" 
                onClick={clearVideo}
              >
                清空
              </button>
            )}
          </div>
        </div>
        
        <div className="main-content">
          {/* 使用教程 */}
          {!videoUrl && (
            <div className="tutorial-section">
              <h2>使用教程</h2>
              <div className="tutorial-steps">
                <div className="tutorial-step">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <h3>下载视频</h3>
                    <p>点击上方的"下载视频"链接，打开B站视频解析网页，下载你想要解析的视频。</p>
                  </div>
                </div>
                <div className="tutorial-step">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <h3>上传视频</h3>
                    <p>点击"解析视频"按钮，在弹出的窗口中选择下载好的视频文件。</p>
                  </div>
                </div>
                <div className="tutorial-step">
                  <div className="step-number">3</div>
                  <div className="step-content">
                    <h3>等待解析</h3>
                    <p>上传完成后，系统会自动解析视频并提取字幕。</p>
                  </div>
                </div>
                <div className="tutorial-step">
                  <div className="step-number">4</div>
                  <div className="step-content">
                    <h3>查看结果</h3>
                    <p>解析完成后，你可以在页面上看到视频播放器和提取的字幕。</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {isUploadModalOpen && (
          <div className="modal-overlay">
            <div className="modal">
              <div className="modal-header">
                <h2>上传视频</h2>
                <button className="close-btn" onClick={closeUploadModal}>&times;</button>
              </div>
              <div className="modal-body">
                <input 
                  type="file" 
                  accept="video/mp4,video/webm,video/ogg,video/mov,video/avi"
                  onChange={handleFileUpload}
                  className="file-input"
                />
                {uploadProgress > 0 && (
                  <div className="progress-container">
                    <div className="progress-label">上传进度: {uploadProgress}%</div>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${uploadProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                {isProcessing && (
                  <div className="progress-container">
                    <div className="progress-label">解析进度: {parsingProgress}%</div>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${parsingProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 视频播放器 */}
        {videoUrl && (
          <div className="subtitles-container">
            <h2>解析结果</h2>
            <div className="video-player-container">
              <div ref={playerRef}></div>
            </div>
            
            {/* 下载按钮 */}
            <div className="download-buttons">
              {subtitles.length > 0 && (
                <button 
                  className="btn btn-download" 
                  onClick={() => downloadSubtitles()}
                >
                  下载字幕
                </button>
              )}
            </div>
            
            {/* 字幕列表 */}
            {subtitles.length > 0 && (
              <div className="subtitles-list">
                {subtitles.map((subtitle, index) => (
                  <div key={index} className="subtitle-item">
                    <span className="subtitle-time">{subtitle.time}</span>
                    <span className="subtitle-text">{subtitle.text}</span>
                  </div>
                ))}
              </div>
            )}
            
            {/* 解析中提示 */}
            {isProcessing && (
              <div className="processing提示">
                <p>正在解析视频，请稍候...</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
