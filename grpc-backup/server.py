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
    def UploadFile(self, request_iterator, context):
        filename = None
        with open(os.path.join(BACKUP_FOLDER, "temp_upload"), "wb") as f:
            for chunk in request_iterator:
                filename = chunk.filename
                f.write(chunk.content)
        if filename:
            os.rename(os.path.join(BACKUP_FOLDER, "temp_upload"), os.path.join(BACKUP_FOLDER, filename))
            return backup_pb2.UploadStatus(success=True, message=f"Arquivo {filename} enviado com sucesso")
        else:
            return backup_pb2.UploadStatus(success=False, message="Nenhum dado recebido")

    def DownloadFile(self, request, context):
        filepath = os.path.join(BACKUP_FOLDER, request.filename)
        if not os.path.exists(filepath):
            context.set_details('Arquivo não encontrado')
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return

        with open(filepath, "rb") as f:
            while chunk := f.read(1024 * 1024):
                yield backup_pb2.FileChunk(filename=request.filename, content=chunk)

    def ListFiles(self, request, context):
        files = os.listdir(BACKUP_FOLDER)
        return backup_pb2.FileList(filenames=files)

    def DeleteFile(self, request, context):
        filepath = os.path.join(BACKUP_FOLDER, request.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return backup_pb2.DeleteStatus(success=True, message="Arquivo deletado com sucesso")
        else:
            return backup_pb2.DeleteStatus(success=False, message="Arquivo não encontrado")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
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