import streamlit as st
import cv2, tempfile, os
from paddleocr import PaddleOCR
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Peony LinguaReel")
st.title("🎬 Peony - Dịch phim có chữ sẵn")

@st.cache_resource
def get_ocr():
    return PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
ocr = get_ocr()

video = st.file_uploader("Up video.mp4", type=["mp4","mov","mkv"])
if video:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(video.read())
    cap = cv2.VideoCapture(tfile.name)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    texts = []
    with st.spinner("Đang đọc chữ Trung..."):
        for i in range(0, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), int(fps)):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret: continue
            h,w = frame.shape[:2]
            crop = frame[int(h*0.65):h, 0:w]
            result = ocr.ocr(crop, cls=True)
            if result and result[0]:
                for line in result[0]:
                    txt = line[1][0]
                    if txt not in texts: texts.append(txt)
    cap.release()
    goc = "\n".join(texts)
    goc = st.text_area("Chữ đọc được (sửa được)", goc, height=200)
    if st.button("Dịch sang tiếng Việt"):
        vi = GoogleTranslator(source='auto', target='vi').translate(goc)
        st.text_area("Bản dịch", vi, height=200)
        st.success("Xong! Đây là web của bạn rồi!")
