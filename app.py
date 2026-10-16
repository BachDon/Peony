import streamlit as st
import cv2, tempfile
from deep_translator import GoogleTranslator
import easyocr

st.set_page_config(page_title="Peony LinguaReel")
st.title("🎬 Peony - Dịch phim có chữ sẵn")
st.caption("Bản nhẹ - chỉ đọc 60s đầu để tránh bị bóp CPU")

@st.cache_resource
def get_ocr():
    return easyocr.Reader(['ch_sim','en'], gpu=False)

reader = get_ocr()

video = st.file_uploader("Up video (nên cắt <50MB, 1-2 phút thôi)", type=["mp4","mov","mkv"])
if video:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(video.read())
    cap = cv2.VideoCapture(tfile.name)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    texts = []
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    max_frames = int(fps * 60)  # chỉ lấy 60s đầu
    check_every = int(fps * 3)  # 3 giây check 1 lần

    with st.spinner("Đang đọc chữ... (bản nhẹ nên nhanh hơn)"):
        progress = st.progress(0)
        for idx, i in enumerate(range(0, min(total_frames, max_frames), check_every)):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret: continue
            # thu nhỏ lại cho nhẹ
            frame = cv2.resize(frame, (640, 360))
            h,w = frame.shape[:2]
            crop = frame[int(h*0.65):h, 0:w]
            result = reader.readtext(crop, detail=0)
            for txt in result:
                if txt not in texts and len(txt)>1: texts.append(txt)
            progress.progress(min(idx/20, 1.0))
    
    cap.release()
    if texts:
        goc = "\n".join(texts)
        goc = st.text_area("Chữ đọc được (sửa được)", goc, height=200)
        if st.button("Dịch sang TV"):
            vi = GoogleTranslator(source='auto', target='vi').translate(goc)
            st.text_area("Bản dịch", vi, height=300)
            st.success("Xong!")
    else:
        st.warning("Không đọc được chữ, thử video khác nét hơn nhé")
