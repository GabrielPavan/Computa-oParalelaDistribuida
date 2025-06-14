import streamlit as st
import grpc
import backup_pb2
import backup_pb2_grpc
import os

# Configurações do cliente gRPC
channel = grpc.insecure_channel('localhost:50051')
stub = backup_pb2_grpc.BackupServiceStub(channel)

st.set_page_config(page_title="Sistema de Backup gRPC", page_icon="💾")

st.title("💾 Sistema de Backup com gRPC")
st.subheader("Interface Web para envio e gerenciamento de arquivos")


# 📤 Upload de Arquivo
st.header("📤 Enviar Arquivo")
uploaded_file = st.file_uploader("Escolha um arquivo para enviar")

if uploaded_file is not None:
    if st.button("Enviar"):
        file_content = uploaded_file.read()
        response = stub.UploadFile(backup_pb2.File(
            filename=uploaded_file.name,
            content=file_content
        ))
        if response.status:
            st.success(f"Arquivo '{uploaded_file.name}' enviado com sucesso!")
        else:
            st.error(f"Erro ao enviar o arquivo '{uploaded_file.name}'")


# 📄 Listar Arquivos
st.header("📄 Arquivos no Servidor")
if st.button("Listar Arquivos"):
    response = stub.ListFiles(backup_pb2.Empty())
    if response.filenames:
        st.write("### Arquivos Disponíveis:")
        for file in response.filenames:
            st.write(f"- {file}")
    else:
        st.info("Nenhum arquivo encontrado no servidor.")


# 📥 Download de Arquivo
st.header("📥 Baixar Arquivo")
download_file = st.text_input("Digite o nome do arquivo para download")

if st.button("Baixar"):
    try:
        response = stub.DownloadFile(backup_pb2.FileRequest(filename=download_file))
        if response.content:
            with open(os.path.join("downloads", download_file), "wb") as f:
                f.write(response.content)
            st.success(f"Arquivo '{download_file}' baixado com sucesso para a pasta 'downloads'.")
        else:
            st.error("Arquivo não encontrado no servidor.")
    except Exception as e:
        st.error(f"Erro no download: {e}")


# 🗑️ Deletar Arquivo
st.header("🗑️ Deletar Arquivo")
delete_file = st.text_input("Digite o nome do arquivo para deletar")

if st.button("Deletar"):
    response = stub.DeleteFile(backup_pb2.FileRequest(filename=delete_file))
    if response.status:
        st.success(f"Arquivo '{delete_file}' deletado com sucesso.")
    else:
        st.error(f"Erro ao deletar o arquivo '{delete_file}' ou arquivo não encontrado.")
