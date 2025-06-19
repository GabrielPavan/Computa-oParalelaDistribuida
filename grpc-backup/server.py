import grpc
from concurrent import futures
import time
import os
import backup_pb2
import backup_pb2_grpc

# Pasta onde os arquivos serão armazenados
BACKUP_FOLDER = "backup_storage"
os.makedirs(BACKUP_FOLDER, exist_ok=True)

class BackupService(backup_pb2_grpc.BackupServiceServicer):
    def UploadFile(self, request, context):
        filename = request.filename
        content = request.content
        try:
            with open(f'backup_storage/{filename}', 'wb') as f:
                f.write(content)
            return backup_pb2.UploadStatus(
                success=True,
                message="Arquivo enviado com sucesso."
            )
        except Exception as e:
            return backup_pb2.UploadStatus(
                success=False,
                message=f"Erro ao salvar arquivo: {e}"
            )
    def DownloadFile(self, request, context):
        filename = request.filename
        try:
            with open(f'backup_storage/{filename}', 'rb') as f:
                content = f.read()

            return backup_pb2.FileChunk(
                filename=filename,
                content=content
            )
        except FileNotFoundError:
            return backup_pb2.FileChunk(
                filename=filename,
                content=b''
            )

    def ListFiles(self, request, context):
        try:
            files = os.listdir('backup_storage')
            return backup_pb2.FileList(filenames=files)
        except Exception as e:
            return backup_pb2.FileList(filenames=[])

    def DeleteFile(self, request, context):
        filename = request.filename
        try:
            os.remove(f'backup_storage/{filename}')
            return backup_pb2.DeleteStatus(
                success=True,
                message="Arquivo deletado com sucesso."
            )
        except FileNotFoundError:
            return backup_pb2.DeleteStatus(
                success=False,
                message="Arquivo não encontrado."
            )
        except Exception as e:
            return backup_pb2.DeleteStatus(
                success=False,
                message=f"Erro ao deletar arquivo: {e}"
            )

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_receive_message_length', 200 * 1024 * 1024), 
            ('grpc.max_send_message_length', 200 * 1024 * 1024),
        ]
    )
    backup_pb2_grpc.add_BackupServiceServicer_to_server(BackupService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Servidor em execução na porta 50051...")
    try:
        while True:
            time.sleep(86400)  # Mantém o servidor rodando
    except KeyboardInterrupt:
        print("Encerrando o servidor...")
        server.stop(0)

if __name__ == '__main__':
    serve()