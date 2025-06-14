import grpc
import backup_pb2
import backup_pb2_grpc
import os

def upload_file(stub, filepath):
    def generate_chunks():
        with open(filepath, "rb") as f:
            while chunk := f.read(1024 * 1024):
                yield backup_pb2.FileChunk(filename=os.path.basename(filepath), content=chunk)

    response = stub.UploadFile(generate_chunks())
    print(response.message)

def download_file(stub, filename):
    with open(filename, "wb") as f:
        for chunk in stub.DownloadFile(backup_pb2.FileRequest(filename=filename)):
            f.write(chunk.content)
    print(f"Arquivo {filename} baixado com sucesso")

def list_files(stub):
    response = stub.ListFiles(backup_pb2.Empty())
    print("\nArquivos no servidor:")
    for file in response.filenames:
        print(f" - {file}")

def delete_file(stub, filename):
    response = stub.DeleteFile(backup_pb2.FileRequest(filename=filename))
    print(response.message)

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = backup_pb2_grpc.BackupServiceStub(channel)
        while True:
            print("\n=== MENU ===")
            print("1. Enviar arquivo")
            print("2. Baixar arquivo")
            print("3. Listar arquivos")
            print("4. Deletar arquivo")
            print("5. Sair")
            choice = input("Escolha: ")

            if choice == "1":
                path = input("Caminho do arquivo para enviar: ")
                if os.path.exists(path):
                    upload_file(stub, path)
                else:
                    print("Arquivo não encontrado.")
            elif choice == "2":
                filename = input("Nome do arquivo para baixar: ")
                download_file(stub, filename)
            elif choice == "3":
                list_files(stub)
            elif choice == "4":
                filename = input("Nome do arquivo para deletar: ")
                delete_file(stub, filename)
            elif choice == "5":
                print("Encerrando cliente...")
                break
            else:
                print("Opção inválida.")

if __name__ == '__main__':
    run()