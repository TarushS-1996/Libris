import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from ingest.ingest import ingest_file, delete_file_from_vector_store
from milvus_helper.vector_store import get_vector_store

class DataDirectoryHandler(FileSystemEventHandler):
    def __init__(self, knowledge_base_updater):
        self.knowledge_base_updater = knowledge_base_updater

    def on_created(self, event):
        if not event.is_directory:
            print(f"File created: {event.src_path}")
            self.knowledge_base_updater('add', event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"File deleted: {event.src_path}")
            self.knowledge_base_updater('remove', event.src_path)

def knowledge_base_updater(action, file_path):
    vector_store = get_vector_store("knowledge_chunks")

    if action == 'add':
        print(f"Processing added file: {file_path}")
        try:
            ingest_file(file_path, vector_store=vector_store, domain="dynamic")
            print(f"✅ Successfully added {file_path} to the vector store.")
        except Exception as e:
            print(f"❌ Failed to add {file_path} to the vector store: {e}")

    elif action == 'remove':
        print(f"Processing removed file: {file_path}")
        try:
            
            delete_file_from_vector_store(file_path, vector_store=vector_store)
            print(f"✅ Successfully removed {file_path} from the vector store.")
        except Exception as e:
            print(f"❌ Failed to remove {file_path} from the vector store: {e}")
        # Add logic to remove the file's data from the knowledge base

def start_file_watcher(path_to_watch="./data"):
    path_to_watch = os.path.join(os.getcwd(), path_to_watch)
    event_handler = DataDirectoryHandler(knowledge_base_updater)
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_file_watcher(path_to_watch="./data")