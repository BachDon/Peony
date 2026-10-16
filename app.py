import streamlit as st
import cv2, tempfile
from deep_translator import GoogleTranslator
import easyocr

st.set_page_config(page_title="Peony LinguaReel")
st.title("🎬 Peony - Dịch phim có chữ sẵn")

@st.cache_resource
def get_ocr():
    return easyocr.Reader(['ch_sim','en'], gpu=False)

reader = get_ocr()

video = st.file_uploader("Up video phim Trung", type=["mp4","mov","mkv"])
if video:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(video.read())
    cap = cv2.VideoCapture(tfile.name)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    texts = []
    with st.spinner("Đang đọc chữ... lần đầu tải model hơi lâu"):
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        for i in range(0, total, int(fps*2)):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret: continue
            h,w = frame.shape[:2]
            crop = frame[int(h*0.65):h, 0:w]
            result = reader.readtext(crop)
            for _, txt, _ in result:
                if txt not in texts: texts.append(txt)
    cap.release()
    goc = "\n".join(texts)
    goc = st.text_area("Chữ đọc được", goc, height=200)
    if st.button("Dịch sang tiếng Việt"):
        vi = GoogleTranslator(source='auto', target='vi').translate(goc)
        st.text_area("Bản dịch", vi, height=300)
        st.success("Xong! Đây chính là web y chang linguareel.com của bạn!")
