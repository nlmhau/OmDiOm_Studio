// ═══════════════════════════════════════════════════════════════
// OmDiOm Studio - VOICE RECORDER & VAD (UI/js/recorder.js)
// ═══════════════════════════════════════════════════════════════

// ═══════════════════════════════════════════════════════════════
// GHI ÂM TRỰC TIẾP + LỌC ĐOẠN GIỌNG SẠCH NHẤT (3–7 GIÂY)
// ═══════════════════════════════════════════════════════════════
(function(){
  const MAX_REC_SEC = 30;
  const MIN_SEG = 3;
  const MAX_SEG = 7;

  let mediaRec = null;
  let audioCtx = null;
  let analyser = null;
  let recStream = null;
  let chunks = [];
  let recStart = 0;
  let recTimerId = null;
  let recLevelId = null;
  let fullBlob = null;
  let bestSegBlob = null;
  let segments = [];

  const btnStart = $('#btnRecStart');
  const btnStop = $('#btnRecStop');
  const btnReset = $('#btnRecReset');
  const btnUse = $('#btnRecUse');
  const elTimer = $('#recTimer');
  const elLevel = $('#recLevel');
  const elTag = $('#recTag');
  const elResult = $('#recResult');
  const elResultInfo = $('#recResultInfo');
  const elSegments = $('#recSegments');
  const elWarn = $('#recSecureWarn');
  const elWarnMsg = $('#recSecureWarnMsg');

  if(!btnStart) return;

  // Kiểm tra nếu đang mở dạng file:// và thiếu mediaDevices thì hiện cảnh báo ngay
  if(location.protocol === 'file:'){
    if(elWarn) elWarn.style.display = 'block';
  }

  function fmtTimer(sec){
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
  }

  function setRecState(state){
    if(state === 'idle'){
      elTag.textContent = 'SẴN SÀNG';
      elTag.className = 'tag';
      elTimer.className = 'rec-timer idle';
      elTimer.textContent = '00:00';
      elLevel.style.width = '0%';
      btnStart.disabled = false;
      btnStart.innerHTML = '🎙️ Bắt đầu ghi';
      btnStart.classList.remove('recording');
      btnStop.disabled = true;
      btnReset.disabled = true;
    } else if(state === 'recording'){
      elTag.textContent = 'ĐANG GHI...';
      elTag.className = 'tag bad';
      elTimer.className = 'rec-timer';
      btnStart.disabled = true;
      btnStart.classList.add('recording');
      btnStart.innerHTML = '🔴 Đang ghi...';
      btnStop.disabled = false;
      btnReset.disabled = true;
    } else if(state === 'done'){
      elTag.textContent = 'ĐÃ GHI XONG';
      elTag.className = 'tag ok';
      elTimer.className = 'rec-timer idle';
      btnStart.disabled = true;
      btnStart.classList.remove('recording');
      btnStop.disabled = true;
      btnReset.disabled = false;
    }
  }

  async function layAudioStream(){
    // 1. Kiểm tra hỗ trợ mediaDevices chuẩn
    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
      try {
        return await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
      } catch(e1) {
        // Thử lại với audio: true cơ bản (tránh lỗi do driver mic từ chối constraints)
        return await navigator.mediaDevices.getUserMedia({ audio: true });
      }
    }
    // 2. Thử API cũ (navigator.getUserMedia / webkitGetUserMedia)
    const legacyGUM = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
    if(legacyGUM){
      return new Promise(function(resolve, reject){
        legacyGUM.call(navigator, { audio: true }, resolve, reject);
      });
    }
    throw new Error('SECURE_CONTEXT_REQUIRED');
  }

  async function batDauGhi(){
    try {
      recStream = await layAudioStream();
      if(elWarn) elWarn.style.display = 'none';
    } catch(e){
      if(e.message === 'SECURE_CONTEXT_REQUIRED' || (location.protocol === 'file:' && (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia))){
        if(elWarn){
          elWarn.style.display = 'block';
          if(elWarnMsg) elWarnMsg.textContent = 'Trình duyệt Chrome/Edge chặn Micro khi mở trực tiếp tệp file://.';
        }
        toast('Chrome chặn Micro trên file://. Vui lòng bấm vào liên kết trong ô để mở http://127.0.0.1:8000', true);
      } else if(e.name === 'NotAllowedError' || e.name === 'PermissionDeniedError'){
        if(elWarn){
          elWarn.style.display = 'block';
          if(elWarnMsg) elWarnMsg.textContent = 'Bạn đã từ chối quyền truy cập Micro trên trình duyệt. Hãy bấm biểu tượng ổ khóa/camera trên thanh địa chỉ để cấp quyền lại.';
        }
        toast('Bạn chưa cấp quyền Micro cho trang web!', true);
      } else {
        toast('Không mở được micro: ' + (e.message || e.name), true);
      }
      return;
    }

    chunks = [];
    fullBlob = null;
    bestSegBlob = null;
    segments = [];
    elResult.classList.remove('show');

    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      audioCtx = new AC();
      const src = audioCtx.createMediaStreamSource(recStream);
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      src.connect(analyser);
    } catch(e){
      console.warn('Lỗi khởi tạo Analyser:', e);
    }

    let recOpts = {};
    if(typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported){
      if(MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) recOpts = {mimeType: 'audio/webm;codecs=opus'};
      else if(MediaRecorder.isTypeSupported('audio/webm')) recOpts = {mimeType: 'audio/webm'};
      else if(MediaRecorder.isTypeSupported('audio/mp4')) recOpts = {mimeType: 'audio/mp4'};
    }

    try {
      mediaRec = new MediaRecorder(recStream, recOpts);
    } catch(_){
      mediaRec = new MediaRecorder(recStream);
    }

    mediaRec.ondataavailable = function(e){ if(e.data && e.data.size > 0) chunks.push(e.data); };
    mediaRec.onstop = function(){ xuLySauGhi(); };

    mediaRec.start(100);
    recStart = performance.now();
    setRecState('recording');

    // Timer cập nhật
    recTimerId = setInterval(function(){
      const elapsed = (performance.now() - recStart) / 1000;
      elTimer.textContent = fmtTimer(elapsed);
      if(elapsed >= MAX_REC_SEC){
        dungGhi();
      }
    }, 200);

    // Thanh mức âm lượng
    if(analyser){
      const dataArr = new Uint8Array(analyser.frequencyBinCount);
      recLevelId = setInterval(function(){
        if(!analyser) return;
        analyser.getByteFrequencyData(dataArr);
        let sum = 0;
        for(let i = 0; i < dataArr.length; i++) sum += dataArr[i];
        const avg = sum / dataArr.length;
        const pct = Math.min(100, (avg / 128) * 100);
        elLevel.style.width = pct + '%';
      }, 60);
    }
  }

  function dungGhi(){
    clearInterval(recTimerId);
    clearInterval(recLevelId);
    if(mediaRec && mediaRec.state === 'recording'){
      mediaRec.stop();
    }
    if(recStream){
      recStream.getTracks().forEach(function(t){ t.stop(); });
    }
    if(audioCtx){
      audioCtx.close().catch(function(){});
      audioCtx = null;
    }
    analyser = null;
    setRecState('done');
  }

  function resetGhi(){
    fullBlob = null;
    bestSegBlob = null;
    segments = [];
    elResult.classList.remove('show');
    elSegments.innerHTML = '';
    setRecState('idle');
  }

  async function xuLySauGhi(){
    if(!chunks.length){
      toast('Không nhận được dữ liệu âm thanh', true);
      resetGhi();
      return;
    }
    fullBlob = new Blob(chunks, {type: chunks[0].type || 'audio/webm'});
    const totalSec = (performance.now() - recStart) / 1000;

    elResult.classList.add('show');
    elResultInfo.textContent = 'Đang phân tích ' + totalSec.toFixed(1) + 's ghi âm...';
    elSegments.innerHTML = '<div class="muted">Đang phân tích độ sạch và tìm đoạn 3–7s tốt nhất...</div>';

    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      const ctx = new AC();
      const arrBuf = await fullBlob.arrayBuffer();
      const audioBuf = await ctx.decodeAudioData(arrBuf);
      const sr = audioBuf.sampleRate;
      const rawData = audioBuf.getChannelData(0);

      // Tính RMS theo từng frame 0.05s
      const frameSize = Math.floor(sr * 0.05);
      const rmsArr = [];
      for(let i = 0; i + frameSize <= rawData.length; i += frameSize){
        let sumSq = 0;
        for(let j = i; j < i + frameSize; j++) sumSq += rawData[j] * rawData[j];
        rmsArr.push(Math.sqrt(sumSq / frameSize));
      }

      // Tìm ngưỡng phân biệt giọng nói vs im lặng
      const sortedRms = rmsArr.slice().sort(function(a,b){return a - b;});
      const silenceThresh = sortedRms[Math.floor(sortedRms.length * 0.3)] * 2.5;

      // Tìm các đoạn liên tục có giọng nói (RMS > ngưỡng)
      const voiceRegions = [];
      let inVoice = false;
      let regionStart = 0;
      for(let i = 0; i < rmsArr.length; i++){
        if(rmsArr[i] > silenceThresh && !inVoice){
          inVoice = true;
          regionStart = i;
        } else if(rmsArr[i] <= silenceThresh && inVoice){
          inVoice = false;
          const startSec = regionStart * 0.05;
          const endSec = i * 0.05;
          if(endSec - startSec >= 0.5){
            voiceRegions.push({start: startSec, end: endSec});
          }
        }
      }
      if(inVoice){
        const startSec = regionStart * 0.05;
        const endSec = rmsArr.length * 0.05;
        if(endSec - startSec >= 0.5) voiceRegions.push({start: startSec, end: endSec});
      }

      // Gộp các đoạn gần nhau (< 0.35s gap)
      const merged = [];
      for(const r of voiceRegions){
        if(merged.length && r.start - merged[merged.length-1].end < 0.35){
          merged[merged.length-1].end = r.end;
        } else {
          merged.push({start: r.start, end: r.end});
        }
      }

      // Tạo candidate segments 3-7s bằng cửa sổ trượt
      const candidates = [];
      for(const region of merged){
        const rDur = region.end - region.start;
        if(rDur >= MIN_SEG && rDur <= MAX_SEG){
          candidates.push({start: region.start, end: region.end, dur: rDur});
        } else if(rDur > MAX_SEG){
          // Cửa sổ trượt
          for(let s = region.start; s + MIN_SEG <= region.end; s += 1.0){
            const e = Math.min(s + MAX_SEG, region.end);
            const d = e - s;
            if(d >= MIN_SEG) candidates.push({start: s, end: e, dur: d});
          }
        }
      }

      // Nếu không đủ đoạn dài, lấy đoạn dài nhất có thể
      if(!candidates.length && merged.length){
        const longest = merged.reduce(function(a,b){return (b.end-b.start) > (a.end-a.start) ? b : a;});
        candidates.push({start: longest.start, end: Math.min(longest.start + MAX_SEG, longest.end), dur: Math.min(longest.end - longest.start, MAX_SEG)});
      }

      // Nếu người nói đều cả đoạn 30s mà không có khoảng lặng ngắt rõ rệt
      if(!candidates.length && audioBuf.duration >= MIN_SEG){
        const maxD = Math.min(audioBuf.duration, MAX_SEG);
        candidates.push({start: 0, end: maxD, dur: maxD});
      }

      // Chấm điểm: ưu tiên RMS cao đều + ít biến thiên + thời lượng gần 5s
      for(const c of candidates){
        const fStart = Math.floor(c.start / 0.05);
        const fEnd = Math.floor(c.end / 0.05);
        const seg = rmsArr.slice(fStart, fEnd);
        const mean = seg.reduce(function(a,b){return a+b;}, 0) / (seg.length || 1);
        const variance = seg.reduce(function(a,b){return a + (b - mean) * (b - mean);}, 0) / (seg.length || 1);
        const stability = 1 / (1 + Math.sqrt(variance) / (mean || 0.001));
        const durationBonus = 1 - Math.abs(c.dur - 5) / 5;
        c.score = (mean * 10 + stability * 5 + durationBonus * 3);
        c.meanRms = mean;
      }

      candidates.sort(function(a,b){return b.score - a.score;});
      segments = candidates.slice(0, 5);

      if(!segments.length){
        elResultInfo.textContent = 'Không tìm được đoạn giọng nói rõ ràng. Hãy thử ghi lại.';
        elSegments.innerHTML = '';
        ctx.close();
        return;
      }

      elResultInfo.textContent = 'Đã tìm được ' + segments.length + ' đoạn tốt nhất (sắp theo chất lượng âm thanh):';

      // Render segments
      let html = '';
      for(let i = 0; i < segments.length; i++){
        const s = segments[i];
        html += '<div class="rec-seg' + (i === 0 ? ' best' : '') + '" data-seg-idx="' + i + '">' +
          '<span class="seg-info">' + (i === 0 ? '⭐ ' : '') + 'Đoạn ' + (i+1) + ': ' + s.start.toFixed(1) + 's → ' + s.end.toFixed(1) + 's (' + s.dur.toFixed(1) + 's)</span>' +
          '<span class="seg-score">Điểm: ' + s.score.toFixed(1) + '</span>' +
          '<button class="mini" data-seg-play="' + i + '" title="Nghe thử đoạn này">▶</button>' +
          '</div>';
      }
      elSegments.innerHTML = html;
      btnUse.disabled = false;

      // Mặc định chọn segment tốt nhất
      let selectedIdx = 0;

      // Tạo blob WAV cho segment đã chọn
      async function taoSegBlob(idx){
        const seg = segments[idx];
        const startSample = Math.floor(seg.start * sr);
        const endSample = Math.min(Math.floor(seg.end * sr), rawData.length);
        const segLen = endSample - startSample;

        const offCtx = new OfflineAudioContext(1, segLen, sr);
        const buf = offCtx.createBuffer(1, segLen, sr);
        buf.getChannelData(0).set(rawData.slice(startSample, endSample));
        const src2 = offCtx.createBufferSource();
        src2.buffer = buf;
        src2.connect(offCtx.destination);
        src2.start();
        const rendered = await offCtx.startRendering();

        // Encode WAV 16-bit PCM
        const wavData = rendered.getChannelData(0);
        const wavBuf = new ArrayBuffer(44 + wavData.length * 2);
        const view = new DataView(wavBuf);
        function writeStr(off, s){for(let i=0;i<s.length;i++) view.setUint8(off+i, s.charCodeAt(i));}
        writeStr(0, 'RIFF');
        view.setUint32(4, 36 + wavData.length * 2, true);
        writeStr(8, 'WAVE');
        writeStr(12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true);
        view.setUint16(22, 1, true);
        view.setUint32(24, sr, true);
        view.setUint32(28, sr * 2, true);
        view.setUint16(32, 2, true);
        view.setUint16(34, 16, true);
        writeStr(36, 'data');
        view.setUint32(40, wavData.length * 2, true);
        for(let i = 0; i < wavData.length; i++){
          const s16 = Math.max(-1, Math.min(1, wavData[i])) * 32767;
          view.setInt16(44 + i * 2, s16, true);
        }
        return new Blob([wavBuf], {type: 'audio/wav'});
      }

      // Gán sự kiện click chọn segment
      elSegments.querySelectorAll('.rec-seg').forEach(function(el){
        el.addEventListener('click', function(e){
          if(e.target.tagName === 'BUTTON') return;
          selectedIdx = parseInt(el.dataset.segIdx);
          elSegments.querySelectorAll('.rec-seg').forEach(function(s){s.classList.remove('best');});
          el.classList.add('best');
        });
      });

      // Gán sự kiện nghe thử segment
      elSegments.querySelectorAll('[data-seg-play]').forEach(function(btn){
        btn.addEventListener('click', async function(e){
          e.stopPropagation();
          const idx = parseInt(btn.dataset.segPlay);
          const segBlob = await taoSegBlob(idx);
          const url = URL.createObjectURL(segBlob);
          const a = new Audio(url);
          a.onended = function(){URL.revokeObjectURL(url);};
          window.AudioManager.play(a);
        });
      });

      // Nút "Dùng đoạn sạch nhất"
      btnUse.onclick = async function(){
        btnUse.disabled = true;
        btnUse.innerHTML = '⏳ Đang nạp clip...';
        bestSegBlob = await taoSegBlob(selectedIdx);

        // Gán vào input file của tab Clone
        const cloneSection = document.getElementById('clone');
        const fileInput = cloneSection.querySelector('[data-file]');
        const dropMain = cloneSection.querySelector('[data-dropmain]');
        const dropSub = cloneSection.querySelector('[data-dropsub]');
        const fileInfo = cloneSection.querySelector('[data-fileinfo]');

        const wavFile = new File([bestSegBlob], 'ghi_am_' + Date.now() + '.wav', {type: 'audio/wav'});

        const dt = new DataTransfer();
        dt.items.add(wavFile);
        fileInput.files = dt.files;
        fileInput.dispatchEvent(new Event('change', {bubbles: true}));

        if(dropMain) dropMain.textContent = '🎙️ ' + wavFile.name;
        if(dropSub) dropSub.textContent = (bestSegBlob.size / 1024).toFixed(0) + ' KB · Ghi âm trực tiếp';
        if(fileInfo) fileInfo.textContent = 'Đoạn ' + (selectedIdx+1) + ': ' + segments[selectedIdx].start.toFixed(1) + 's → ' + segments[selectedIdx].end.toFixed(1) + 's (' + segments[selectedIdx].dur.toFixed(1) + 's) · Điểm: ' + segments[selectedIdx].score.toFixed(1);

        btnUse.innerHTML = '✓ Đã nạp clip mẫu từ ghi âm!';
        toast('Đã nạp đoạn sạch nhất (' + segments[selectedIdx].dur.toFixed(1) + 's) làm clip mẫu');
      };

      ctx.close();
    } catch(e){
      elResultInfo.textContent = 'Lỗi phân tích: ' + e.message;
      console.error('Lỗi phân tích ghi âm:', e);
    }
  }

  btnStart.addEventListener('click', batDauGhi);
  btnStop.addEventListener('click', dungGhi);
  btnReset.addEventListener('click', resetGhi);
})();


