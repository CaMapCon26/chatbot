import streamlit as st
import openai
import os
from dotenv import load_dotenv
import PyPDF2
import io

# Tải biến môi trường
load_dotenv()

# Thiết lập cấu hình trang
st.set_page_config(page_title="Simple ChatGPT Chatbot", page_icon="🤖", layout="wide")


def extract_text_from_pdf(pdf_file):
    """Hàm trích xuất văn bản từ file PDF hoặc TXT đã tải lên.
    Đầu vào là file đã tải lên, đầu ra là chuỗi văn bản"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.Bytes10(pdf_file.read()))
        text=""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error("Không thể trích xuất văn bản từ file PDF: {e}")
        return


def create_context_message(context_text, tone=""):
    """Tạo thông điệp hệ thống với context.
    Đầu vào là văn bản context và vai trò, đầu ra là chuỗi thông điệp hệ thống"""
    base_prompt = "Bạn là một trợ lý AI thông minh và thân thiện."
    if tone:
        base_prompt += f" Hãy trả lời với tong giọng {tone}."
    if context_text:
        base_prompt += f"Tham khảo những thông tin sau khi trả lời:\n\n{context_text}\n\nHãy sử dụng thông tin này để trả lời câu hỏi của người dùng một cách chính xác và chi tiết."
    return base_prompt


def initialize_openai():
    """Khởi tạo client OpenAI với khóa API.
    Đầu ra là client OpenAI đã khởi tạo"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("Vui lòng cung cấp khóa API OpenAI trong biến môi trường OPENAI_API_KEY.")
        st.stop()
    client = openai.Client(api_key=api_key)
    return client


def get_chatgpt_response(messages, client=None):
    """Lấy phản hồi từ API ChatGPT.
    Đầu vào là danh sách tin nhắn, đầu ra là phản hồi từ ChatGPT"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Không thể lấy phản hồi từ ChatGPT: {e}")
    return


def main():
    # Khởi tạo client OpenAI
    openai_client = initialize_openai()

    # Tiêu đề và mô tả với st.title và st.markdown
    st.title("🤖 Simple ChatGPT Chatbot")
    st.markdown(
        "Chào mừng bạn đến với trợ lý AI cá nhân của mình! Hãy hỏi tôi bất cứ điều gì."
    )

    # Tạo box hướng dẫn với st.expander và st.markdown
    ##### CODE SNIPPET START #####

    # Khởi tạo trạng thái phiên cho lịch sử cuộc trò chuyện
    # Dùng st.session_state để lưu trữ trạng thái cuộc trò chuyện
    ##### CODE SNIPPET START #####
    if "messages" not in st.session_state:
        st.session_state.messages = [
            { "role": "system", "content": "Bạn là một trợ lý AI thông minh và thân thiện." }
        ]
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "system_message" not in st.session_state:
        st.session_state.system_message = "Bạn là một trợ lý AI thông minh và thân thiện."
        
    
    # Khởi tạo sidebar với st.sidebar
    ##### CODE SNIPPET START #####
    with st.expander("📖 Hướng dẫn sử dụng"):\
        st.markdown("""
            **Cách thêm context vào chatbot:**
            1. **Chọn tone giọng**: Chọn tone giọng cho AI trong sidebar (bình thường, hài hước, nghiêm túc...)
            2. **Nhập text**: Viết thông tin tham khảo vào ô "Nhập context"
            3. **Upload file**: Tải lên file .txt hoặc .pdf chứa thông tin
            4. **Bắt đầu chat**: AI sẽ trả lời dựa trên context bạn cung cấp
            
            **Ví dụ context:**
            - Thông tin về công ty, sản phẩm
            - Tài liệu hướng dẫn, quy trình
            - Kiến thức chuyên môn cụ thể
            - Dữ liệu để phân tích
        """)
    with st.sidebar:
        st.header("⚙️ Cài đặt")

        # Mục Context
        st.subheader("📚 Thêm Context")

        # Chọn tone giọng AI
        # Tạo dropdown menu với st.selectbox
        tone_options = ["Trung tính", "Thân thiện", "Chuyên nghiệp", "Hài hước"]
        selected_tone = st.selectbox(
            "Chọn tone giọng AI",
            options=tone_options,
            key="tone_select",
            index=0,
        )

                # Nhập context thù công bằng text area
        context_text= st.text_area(
            "Nhập context cho AI (nếu có):",
            height=150,
            placeholder="Nhập thông tin hoặc đường dẫn cho AI tại đây...",
            value=(st.session_state.get("context_input", "")),
            key="context_input",
        )

        # Hiển thị độ dài context và nút xóa context
        if context_text:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Độ dài context:** {len(context_text)} ký tự")
            with col2:
                if st.button("🗑️", key="clear_context"):
                    st.session_state.context_input = ""
                    st.experimental_rerun()  # để xóa ngay

        # Tải lên file context nếu không muốn nhập tay
        # Hỗ trợ file .txt và .pdf
        uploaded_file = st.file_uploader(
            "Tải lên file context(txt or pdf)",
            type=["txt", "pdf"],  # ✅ sửa từ typep -> type
            key="file_uploader"
        )

        # Xử lý file đã tải lên và thêm vào file_context
        file_context=""
        if uploaded_file is not None:
            if uploaded_file.type == "text/plain":
                file_context = uploaded_file.getvalue().decode("utf-8")  # ✅ sửa tên biến
                st.success("Đã tải lên file TXT thành công!")
            elif uploaded_file.type == "application/pdf":
                file_context = extract_text_from_pdf(uploaded_file)  # ✅ sửa tên biến
                if file_context:
                    st.success("Đã tải lên file PDF thành công!")
                else:
                    st.error("Không thể trích xuất văn bản từ file PDF!")

        # Kết hợp context từ text area và file
        full_context= ""
        if context_text:
            full_context += context_text + "\n"
        if file_context:
            full_context += file_context + "\n"

        # Cập nhật thông điệp cho hệ thống nếu context thay đổi
        if full_context:
            system_message = create_context_message(full_context, selected_tone)
            if (
                "system_message" not in st.session_state
                or st.session_state.system_message != system_message
            ):
                st.session_state.system_message = system_message
                st.session_state.messages = [
                    {"role": "system", "content": system_message}
                ]
                st.session_state.chat_history = []
                st.success("Đã cập nhật context cho AI!")
                

        # Tạo nút xóa cuộc trò chuyện và giữ nguyên thông điệp hệ thống
        st.button("🗑️ Xóa cuộc trò chuyện", key="clear_chat")

        # Hiển thị context hiện tại nếu có
        if full_context:
            with st.expander("Xem context hiện tại"):
                st.text_area("Context hiện tại:",
                             value=full_context,
                             height=300,
                             disabled=True,
                )

        # Hiện thị tone giọng hiện tại nếu có
        if selected_tone:
            st.info(f"Tone giọng hiện tại: {selected_tone}")  # ✅ sửa f-string


        st.markdown("---")
        st.markdown("🎭 Made by [BaPhong](https://www.facebook.com/im.fong26)")

    # Hiển thị lịch sử trò chuyện trong st.session_state.chat_history với st.markdown
    for i,(user_msg, ai_msg) in enumerate(st.session_state.chat_history):
        if user_msg:
            st.markdown(f"**bạn:**{user_msg}")
            
        if ai_msg:
            st.markdown(f"**AI:** {ai_msg}")

    # Đầu vào câu hỏi từ người dùng với st.chat_input
    user_input = st.chat_input(
        placeholder="Hãy hỏi tôi bất cứ điều gì...",
        key="user_input",
    )
    
    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        with st.spinner("Đang xử lý..."):
            response = get_chatgpt_response(
                st.session_state.messages, client=openai_client
            )

        if response:
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )
            st.session_state.chat_history.append((user_input, response))

        st.rerun()


if __name__ == "__main__":
    main()
