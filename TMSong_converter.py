# Add copyright and tool information at the top of the file
__author__ = "shaneomac"
__copyright__ = "Copyright (c) 2024 Martin Pěnkava - Dobřany"
__license__ = "MIT"
__version__ = "1.0"

import sys
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import mutagen
import subprocess
import re
import paramiko
import webbrowser
import threading
import queue
import time
import io
import requests
from bs4 import BeautifulSoup
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
import tkinter as tk
from tkinter import ttk
import pygame
import urllib.parse
from io import BytesIO
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.flac import FLAC
import zipfile
import shutil
from pathlib import Path
from pathvalidate import sanitize_filename


class ProgressFile(io.BytesIO):
    def __init__(self, *args, **kwargs):
        self._callback = kwargs.pop('callback', None)
        self._size = kwargs.pop('size', 0)
        self._progress = 0
        io.BytesIO.__init__(self, *args, **kwargs)

    def read(self, size):
        data = io.BytesIO.read(self, size)
        self._progress += len(data)
        if self._callback:
            self._callback(self._progress, self._size)
        return data

class AudioConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"Audio Converter for Trackmania 2020 - Tool by {__author__}")
        self.geometry("600x650")  # Increased height to accommodate progress bar

        self.folder_path = ctk.StringVar()
        self.language = ctk.StringVar(value="English")
        self.progress_var = ctk.DoubleVar()  # Initialize progress_var here
        self.progress_var.set(0)
        
        self.translations = {
            "English": {
                "title": "Audio Converter",
                "select_folder": "Select Folder containing audio files (supported formats: .flac, .mp3):",
                "browse": "Browse",
                "convert": "Convert",
                "warning": "Warning",
                "select_folder_msg": "Please select a folder",
                "conversion_complete": "Conversion Complete",
                "conversion_summary": "Successfully converted {} out of {} files.",
                "for_trackmania": "For Trackmania 2020",
                "tool_info": "This tool converts audio files for use in Trackmania 2020",
                "upload": "Upload to Komplexaci Server",
                "upload_complete": "Upload Complete",
                "upload_summary": "Successfully uploaded {} out of {} files.",
                "upload_failed": "Upload Failed",
                "upload_failed_summary": "Failed to upload {} out of {} files.",
                "verify_upload": "Please verify your uploaded files",
                "verify_upload_msg": "Your files have been uploaded, it is there buddy. Please check if you can see them at https://komplexaci.cz/music/",
                "uploading": "Uploading...",
                "update_songs": "Update Song List",
                "success": "Success",
                "songs_updated": "Song list has been updated successfully.",
                "error": "Error",
                "update_failed": "Failed to update song list",
                "enter_metadata": "Enter Metadata",
                "enter_artist": "Enter artist for {}:",
                "enter_title": "Enter title for {}:",
                "enter_album": "Enter album for {}:",
                "conversion_incomplete": "Conversion Incomplete",
                "conversion_incomplete_msg": "Successfully converted {} out of {} files.\nThe following files were not converted:\n{}",
                "metadata_missing_title": "Metadata Missing",
                "metadata_missing_msg": "Metadata not found for {}. Please enter it manually to keep your music files organized on the Trackmania Server.",
                "quality_reminder_title": "Audio Quality Reminder",
                "quality_reminder_msg": "For the best results, please use high-quality MP3 or FLAC files. Avoid using low-quality files or shitty YouTube conversions.",
                "base_upload_failed": "Failed to upload base.py file to the server.",
                "restart_server": "Restart Server",
                "server_restarted": "Server restarted successfully.",
                "server_restart_failed": "Failed to restart the server. Please check the logs or restart manually.",
                "songs_updated_and_restarted": "Song list updated and server restarted successfully.",
                "songs_updated_restart_failed": "Song list updated but server restart failed. Please restart manually.",
                "browse_songs": "Browse Songs",
            },
            "Čeština": {
                "title": "Převodník Zvuku",
                "select_folder": "Vyberte složku která obsahuje zvukové soubory (podporované formáty: .flac, .mp3):",
                "browse": "Procházet",
                "convert": "Převést",
                "warning": "Varování",
                "select_folder_msg": "Prosím vyberte složku",
                "conversion_complete": "Převod Dokončen",
                "conversion_summary": "Úspěšně převedeno {} z {} souborů.",
                "for_trackmania": "Pro Trackmania 2020",
                "tool_info": "Tento nástroj převádí zvukové soubory pro použití v Trackmania 2020",
                "upload": "Nahrát na Komplexácký Server",
                "upload_complete": "Nahrávání Dokončeno",
                "upload_summary": "Úspěšně nahráno {} z {} souborů.",
                "upload_failed": "Nahrávání Selhalo",
                "upload_failed_summary": "Nepodařilo se nahrát {} z {} souborů.",
                "verify_upload": "Prosím ověřte nahrané soubory",
                "verify_upload_msg": "Vaše soubory byly nahrány Je to tam bráško. Prosím zkontrolujte, zda je vidíte na https://komplexaci.cz/music/",
                "uploading": "Nahrávání...",
                "update_songs": "Aktualizovat Seznam Skladeb",
                "success": "Úspěch",
                "songs_updated": "Seznam skladeb byl úspěšně aktualizován.",
                "error": "Chyba",
                "update_failed": "Nepodařilo se aktualizovat seznam skladeb",
                "enter_metadata": "Zadejte metadata",
                "enter_artist": "Zadejte umělce pro {}:",
                "enter_title": "Zadejte název pro {}:",
                "enter_album": "Zadejte album pro {}:",
                "conversion_incomplete": "Převod Nekompletní",
                "conversion_incomplete_msg": "Úspěšně převedeno {} z {} souborů.\nNásledující soubory nebyly převedeny:\n{}",
                "metadata_missing_title": "Chybějící Metadata",
                "metadata_missing_msg": "Metadata nebyla nalezena pro {}. Prosím, zadejte je ručně pro lepší organizaci vašich hudebních souborů na Trackmania Serveru.",
                "quality_reminder_title": "Připomenutí Kvality Zvuku",
                "quality_reminder_msg": "Pro nejlepší výsledky použijte prosím vysoce kvalitní MP3 nebo FLAC soubory. Vyhněte se použití nízko kvalitních souborů nebo shitovejch konverzí z YouTube.",
                "base_upload_failed": "Nepodařilo se nahrát soubor base.py na server.",
                "restart_server": "Restartovat Server",
                "server_restarted": "Server byl úspěšně restartován.",
                "server_restart_failed": "Nepodařilo se restartovat server. Prosím zkontrolujte logy nebo restartujte manuálně.",
                "songs_updated_and_restarted": "Seznam skladeb aktualizován a server úspěšně restartován.",
                "songs_updated_restart_failed": "Seznam skladeb aktualizován, ale restart serveru selhal. Prosím restartujte manuálně.",
                "browse_songs": "Procházet Skladby",
            }
        }

        self.widgets = {}
        self.create_widgets()
        self.progress_queue = queue.Queue()

    def create_widgets(self):
        lang = self.language.get()
        
        self.title(f"{self.translations[lang]['title']} for Trackmania 2020 - Tool by {__author__}")
        
        # Clear existing widgets
        for widget in self.widgets.values():
            widget.destroy()
        
        # Add Trackmania 2020 label
        self.widgets["trackmania_label"] = ctk.CTkLabel(self, text=self.translations[lang]["for_trackmania"])
        self.widgets["trackmania_label"].pack(pady=5)
        
        self.widgets["select_folder_label"] = ctk.CTkLabel(self, text=self.translations[lang]["select_folder"])
        self.widgets["select_folder_label"].pack(pady=10)
        
        self.widgets["folder_entry"] = ctk.CTkEntry(self, textvariable=self.folder_path, width=300)
        self.widgets["folder_entry"].pack()
        
        self.widgets["browse_button"] = ctk.CTkButton(self, text=self.translations[lang]["browse"], command=self.browse_folder)
        self.widgets["browse_button"].pack(pady=10)
        
        self.widgets["convert_button"] = ctk.CTkButton(self, text=self.translations[lang]["convert"], command=self.convert_files)
        self.widgets["convert_button"].pack(pady=10)
        
        # Upload button
        self.widgets["upload_button"] = ctk.CTkButton(self, text=self.translations[lang]["upload"], command=self.upload_files)
        self.widgets["upload_button"].pack(pady=10)

        # Progress bar
        self.widgets["progress_bar"] = ctk.CTkProgressBar(self, variable=self.progress_var, width=300)
        self.widgets["progress_bar"].pack(pady=5)
        self.widgets["progress_bar"].pack_forget()  # Hide initially

        # Progress label
        self.widgets["progress_label"] = ctk.CTkLabel(self, text="")
        self.widgets["progress_label"].pack(pady=5)
        self.widgets["progress_label"].pack_forget()  # Hide initially

        # Trackmania 2020 info
        self.widgets["trackmania_info"] = ctk.CTkLabel(self, text=self.translations[lang]["tool_info"])
        self.widgets["trackmania_info"].pack(side="bottom", pady=5)

        # Copyright information
        self.widgets["copyright_label"] = ctk.CTkLabel(self, text=__copyright__)
        self.widgets["copyright_label"].pack(side="bottom", pady=10)

        # Language switch
        self.widgets["language_menu"] = ctk.CTkOptionMenu(self, values=["English", "Čeština"], variable=self.language, command=self.change_language)
        self.widgets["language_menu"].pack(side="bottom", pady=10)

        # Add a new button for updating the song list
        self.widgets["update_songs_button"] = ctk.CTkButton(self, text=self.translations[self.language.get()]["update_songs"], command=self.update_song_list)
        self.widgets["update_songs_button"].pack(pady=10)

        # Add a new button for restarting the server
        self.widgets["restart_server_button"] = ctk.CTkButton(
            self, 
            text=self.translations[self.language.get()]["restart_server"],
            command=self.restart_server_command
        )
        self.widgets["restart_server_button"].pack(pady=10)

        # Add a new button to browse songs
        self.widgets["browse_songs_button"] = ctk.CTkButton(
            self, 
            text=self.translations[self.language.get()]["browse_songs"],
            command=self.open_song_browser
        )
        self.widgets["browse_songs_button"].pack(pady=10)

    def change_language(self, new_lang):
        self.language.set(new_lang)
        self.create_widgets()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        self.folder_path.set(folder)

    def convert_files(self):
        lang = self.language.get()
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning(self.translations[lang]["warning"], 
                                   self.translations[lang]["select_folder_msg"])
            return

        # Show quality reminder message
        messagebox.showinfo(
            self.translations[lang]["quality_reminder_title"],
            self.translations[lang]["quality_reminder_msg"]
        )

        converted_count = 0
        total_files = 0
        failed_files = []

        for root, dirs, files in os.walk(folder):
            for filename in files:
                if filename.lower().endswith(('.flac', '.mp3')):
                    total_files += 1
                    file_path = os.path.join(root, filename)
                    try:
                        new_filepath = self.convert_to_ogg(file_path)
                        converted_count += 1
                    except ValueError as e:
                        print(f"Skipped conversion: {str(e)}")
                        failed_files.append(filename)
                    except Exception as e:
                        print(f"Error converting {filename}: {str(e)}")
                        failed_files.append(filename)

        if failed_files:
            failed_msg = "\n".join(failed_files)
            messagebox.showwarning(self.translations[lang]["conversion_incomplete"],
                                   self.translations[lang]["conversion_incomplete_msg"].format(
                                       converted_count, total_files, failed_msg))
        else:
            messagebox.showinfo(self.translations[lang]["conversion_complete"], 
                                self.translations[lang]["conversion_summary"].format(converted_count, total_files))

    def convert_to_ogg(self, file_path):
        output_path = os.path.splitext(file_path)[0] + '.ogg'
        
        # Get existing metadata
        metadata = self.get_metadata(file_path)
        
        try:
            # Check for missing metadata and prompt user if necessary
            metadata = self.check_and_prompt_metadata(metadata, os.path.basename(file_path))
        except ValueError as e:
            # User cancelled input, raise error to skip conversion
            raise ValueError(f"Conversion cancelled for {file_path}: {str(e)}")
        
        # Remove pictures from the original file
        self.remove_pictures(file_path)
        
        # Ensure FFmpeg is available
        ffmpeg_path = self.ensure_ffmpeg()
        if not ffmpeg_path:
            raise ValueError("FFmpeg is not available and could not be downloaded.")
        
        command = [
            ffmpeg_path,
            '-i', file_path,
            '-c:a', 'libvorbis',
            '-q:a', '6',
            '-vn',  # This option tells ffmpeg to disable video (including album art)
            '-y',
            output_path
        ]
        
        subprocess.run(command, check=True)
        
        self.set_metadata(output_path, metadata)
        
        # Rename the file
        artist = sanitize_filename(metadata.get('artist', 'Unknown')).replace(' ', '_')
        title = sanitize_filename(metadata.get('title', os.path.splitext(os.path.basename(file_path))[0])).replace(' ', '_')
        new_filename = f"{artist}-{title}.ogg"
        new_filepath = os.path.join(os.path.dirname(output_path), new_filename)
        
        # If the file already exists, overwrite it
        if os.path.exists(new_filepath):
            os.remove(new_filepath)
        os.rename(output_path, new_filepath)
        
        return new_filepath
    
    def sanitize_filename(filename):
        # Remove or replace illegal filename characters and spaces
        filename = re.sub(r'[<>:"/\\|?*\s]', '', filename)
        # Remove any leading/trailing periods
        filename = filename.strip('.')
        return filename

    def remove_spaces(self, text):
        # Remove spaces without replacing them
        return re.sub(r'\s+', '', text)

    def get_metadata(self, file_path):
        metadata = {'artist': '', 'title': '', 'album': ''}
        try:
            if file_path.lower().endswith('.mp3'):
                audio = EasyID3(file_path)
            elif file_path.lower().endswith('.flac'):
                audio = FLAC(file_path)
            else:
                audio = mutagen.File(file_path, easy=True)
            
            if audio is not None:
                for field in metadata.keys():
                    metadata[field] = audio.get(field, [''])[0]
        except Exception as e:
            print(f"Error reading metadata from {file_path}: {str(e)}")
        
        return metadata

    def check_and_prompt_metadata(self, metadata, filename):
        lang = self.language.get()
        fields = ['artist', 'title', 'album']
        
        for field in fields:
            if not metadata[field]:
                value = ctk.CTkInputDialog(
                    title=self.translations[lang]["enter_metadata"],
                    text=self.translations[lang][f"enter_{field}"].format(filename)
                ).get_input()
                if value:
                    metadata[field] = value
                else:
                    # User cancelled input, raise error
                    raise ValueError(f"User cancelled input for {field}")
        
        return metadata

    def set_metadata(self, file_path, metadata):
        audio = mutagen.File(file_path, easy=True)
        
        if audio is not None:
            # Clear existing metadata
            audio.clear()
            
            # Set only the desired metadata fields
            for field, value in metadata.items():
                audio[field] = value
            
            audio.save()

    def remove_pictures(self, file_path):
        if file_path.lower().endswith('.mp3'):
            try:
                audio = ID3(file_path)
                audio.delall("APIC")  # Remove all picture frames
                audio.save()
            except ID3NoHeaderError:
                pass  # File doesn't have an ID3 tag
        elif file_path.lower().endswith('.flac'):
            audio = FLAC(file_path)
            audio.clear_pictures()
            audio.save()

    def upload_to_server(self, local_file_path):
        # SFTP server details
        hostname = 'komplexaci.cz'
        username = 'nasratpico'
        password = 'tourcitetyzmrde' # these are not real passwords, just to be clear, i am not an idiot..
        remote_dir = '/var/www/music/'  # Added trailing slash

        def progress_callback(progress, total):
            self.progress_queue.put(('file_progress', progress, total))

        try:
            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=hostname, username=username, password=password)

            # Create SFTP client
            sftp_client = ssh_client.open_sftp()

            # Check if the remote directory exists, create it if not
            try:
                sftp_client.stat(remote_dir)
            except IOError:
                sftp_client.mkdir(remote_dir)

            # Prepare the file for upload with progress reporting
            file_size = os.path.getsize(local_file_path)
            with open(local_file_path, 'rb') as local_file:
                progress_file = ProgressFile(local_file.read(), size=file_size, callback=progress_callback)

            # Upload the file
            remote_file_path = remote_dir + os.path.basename(local_file_path)
            sftp_client.putfo(progress_file, remote_file_path)

            # Check if the file was uploaded successfully
            if sftp_client.stat(remote_file_path):
                print(f"Successfully uploaded {local_file_path} to {remote_file_path}")
                success = True
            else:
                print(f"Failed to upload {local_file_path}")
                success = False

            # Close the connections
            sftp_client.close()
            ssh_client.close()

            return success
        except Exception as e:
            print(f"Error uploading {local_file_path}: {str(e)}")
            return False

    def upload_files(self):
        if not self.folder_path.get():
            messagebox.showwarning(self.translations[self.language.get()]["warning"],
                                   self.translations[self.language.get()]["select_folder_msg"])
            return

        # Show progress label
        self.show_progress()

        # Start the upload process in a separate thread
        threading.Thread(target=self._upload_files_thread, daemon=True).start()
        self.after(50, self.check_progress_queue)  # Check progress more frequently

    def _upload_files_thread(self):
        folder = self.folder_path.get()
        uploaded_count = 0
        failed_count = 0
        total_files = sum(1 for root, dirs, files in os.walk(folder) 
                          for filename in files if filename.lower().endswith('.ogg'))

        for root, dirs, files in os.walk(folder):
            for filename in files:
                if filename.lower().endswith('.ogg'):
                    file_path = os.path.join(root, filename)
                    try:
                        self.progress_queue.put(('file_start', filename))
                        if self.upload_to_server(file_path):
                            uploaded_count += 1
                        else:
                            failed_count += 1
                    except Exception as e:
                        print(f"Error uploading {filename}: {str(e)}")
                        failed_count += 1
                    
                    self.progress_queue.put(('file_end', uploaded_count, failed_count, total_files))

        # Upload complete
        self.progress_queue.put(None)

    def check_progress_queue(self):
        try:
            progress_data = self.progress_queue.get_nowait()
            if progress_data is None:
                self.upload_complete()
            elif progress_data[0] == 'file_start':
                self.update_progress_start_file(progress_data[1])
            elif progress_data[0] == 'file_progress':
                self.update_progress_file(progress_data[1], progress_data[2])
            elif progress_data[0] == 'file_end':
                self.update_progress_end_file(*progress_data[1:])
            self.after(50, self.check_progress_queue)  # Check progress more frequently
        except queue.Empty:
            self.after(50, self.check_progress_queue)  # Check progress more frequently

    def update_progress_start_file(self, filename):
        lang = self.language.get()
        self.progress_var.set(0)  # Reset progress bar for new file
        self.widgets["progress_label"].configure(text=f"{self.translations[lang]['uploading']} {filename}")

    def update_progress_file(self, progress, total):
        lang = self.language.get()
        percentage = (progress / total) * 100 if total > 0 else 0
        self.progress_var.set(percentage / 100)  # Update progress bar
        self.widgets["progress_label"].configure(text=f"{self.translations[lang]['uploading']} {percentage:.2f}%")

    def update_progress_end_file(self, uploaded_count, failed_count, total_files):
        lang = self.language.get()
        progress = (uploaded_count + failed_count) / total_files if total_files > 0 else 0
        self.progress_var.set(progress)  # Update progress bar
        progress_text = f"{self.translations[lang]['uploading']} {progress*100:.2f}% ({uploaded_count + failed_count}/{total_files})"
        self.widgets["progress_label"].configure(text=progress_text)

    def upload_complete(self):
        self.hide_progress()
        lang = self.language.get()
        
        # Get the last progress update from the label
        progress_text = self.widgets["progress_label"].cget("text")
        uploaded_count = int(progress_text.split('(')[1].split('/')[0])
        total_files = int(progress_text.split('/')[-1].split(')')[0])
        failed_count = total_files - uploaded_count

        if failed_count == 0:
            messagebox.showinfo(self.translations[lang]["upload_complete"],
                                self.translations[lang]["upload_summary"].format(uploaded_count, total_files))
        else:
            messagebox.showwarning(self.translations[lang]["upload_failed"],
                                   self.translations[lang]["upload_failed_summary"].format(failed_count, total_files))

        # Open browser and ask user to verify uploaded files
        webbrowser.open('https://komplexaci.cz/music/')
        messagebox.showinfo(self.translations[lang]["verify_upload"],
                            self.translations[lang]["verify_upload_msg"])

    def show_progress(self):
        self.widgets["progress_bar"].pack(pady=5)
        self.widgets["progress_label"].pack(pady=5)

    def hide_progress(self):
        self.widgets["progress_bar"].pack_forget()
        self.widgets["progress_label"].pack_forget()

    def update_song_list(self):
        try:
            # Fetch the webpage
            response = requests.get('https://www.komplexaci.cz/music/')
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all links that end with .ogg
            ogg_files = [link.get('href') for link in soup.find_all('a') if link.get('href', '').endswith('.ogg')]

            # Construct full URLs
            full_urls = [f"https://www.komplexaci.cz/music/{file}" for file in ogg_files]

            # Generate new base.py file
            self.generate_new_base_file(full_urls)

            # Upload the new base.py file
            if self.upload_base_file():
                messagebox.showinfo(self.translations[self.language.get()]["success"], 
                                    self.translations[self.language.get()]["songs_updated"])
            else:
                messagebox.showerror(self.translations[self.language.get()]["error"], 
                                     self.translations[self.language.get()]["base_upload_failed"])
        except Exception as e:
            messagebox.showerror(self.translations[self.language.get()]["error"], 
                                 f"{self.translations[self.language.get()]['update_failed']}: {str(e)}")

    def generate_new_base_file(self, urls):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.realpath(__file__))
        
        # Set paths relative to the script directory
        template_path = os.path.join(script_dir, 'base_template.py')
        output_path = os.path.join(script_dir, 'base.py')

        # Check if the template file exists
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")

        # Read the template
        with open(template_path, 'r') as file:
            content = file.read()

        # Create the SONGS dictionary
        songs_dict = "SONGS = {\n    'default': [\n"
        for url in urls:
            songs_dict += f"        \"{url}\",\n"
        songs_dict += "    ]\n}"

        # Append the SONGS dictionary to the content
        content += "\n\n" + songs_dict

        # Write the new base.py file
        with open(output_path, 'w') as file:
            file.write(content)

        print(f"New base.py file generated at: {output_path}")

    def upload_base_file(self):
        # SFTP server details
        hostname = 'komplexaci.cz'
        username = 'vylizte'
        password = 'miprdel'
        remote_dir = '/var/lib/docker/volumes/trackmaniaserver_pyplanetData/_data/settings/'
        local_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'base.py')

        try:
            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=hostname, username=username, password=password)

            # Create SFTP client
            sftp_client = ssh_client.open_sftp()

            # Upload the file
            remote_file_path = os.path.join(remote_dir, 'base.py')
            sftp_client.put(local_file, remote_file_path)

            # Close the connections
            sftp_client.close()
            ssh_client.close()

            print(f"Successfully uploaded base.py to {remote_file_path}")
            return True
        except Exception as e:
            print(f"Error uploading base.py: {str(e)}")
            return False

    def restart_server_command(self):
        lang = self.language.get()
        if self.restart_server():
            messagebox.showinfo(
                self.translations[lang]["success"],
                self.translations[lang]["server_restarted"]
            )
        else:
            messagebox.showerror(
                self.translations[lang]["error"],
                self.translations[lang]["server_restart_failed"]
            )

    def restart_server(self):
        # Server details
        hostname = 'komplexaci.cz'
        username = 'nereknu'
        password = 'polibmiprdel'
        restart_command = 'docker restart trackmaniaserver-pyplanet-1'

        try:
            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=hostname, username=username, password=password)

            # Execute the restart command
            stdin, stdout, stderr = ssh_client.exec_command(restart_command)
            
            # Wait for the command to complete
            exit_status = stdout.channel.recv_exit_status()

            # Close the connection
            ssh_client.close()

            if exit_status == 0:
                print("Server restarted successfully")
                return True
            else:
                error_message = stderr.read().decode('utf-8')
                print(f"Failed to restart server. Error: {error_message}")
                return False

        except Exception as e:
            print(f"Error restarting server: {str(e)}")
            return False

    def open_song_browser(self):
        song_browser = SongBrowser(self)
        self.withdraw()  # Hide the main window
        song_browser.protocol("WM_DELETE_WINDOW", lambda: self.on_song_browser_close(song_browser))

    def on_song_browser_close(self, song_browser):
        song_browser.destroy()
        self.deiconify()  # Show the main window again

    def ensure_ffmpeg(self):
        ffmpeg_path = self.get_ffmpeg_path()
        if ffmpeg_path:
            return ffmpeg_path

        # Ask user for permission to download FFmpeg
        if not messagebox.askyesno("FFmpeg Required", 
                                   "FFmpeg is required for audio conversion but is not found on your system. "
                                   "Would you like to download and install it automatically?"):
            return None

        # FFmpeg not found, download it
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        zip_path = os.path.join(os.path.dirname(sys.executable), "ffmpeg.zip")
        extract_path = os.path.join(os.path.dirname(sys.executable), "ffmpeg_temp")

        try:
            # Download FFmpeg with progress
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 KB
            downloaded = 0

            with open(zip_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    size = f.write(data)
                    downloaded += size
                    percent = int(downloaded * 100 / total_size)
                    
                    # Update progress every 10%
                    if percent % 10 == 0:
                        print(f"Downloading FFmpeg: {percent}% complete")
                        # You can also update a progress bar here if you have one in your GUI

            print("Download complete. Extracting files...")

            # Extract FFmpeg
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            # Find and move the executables
            script_dir = os.path.dirname(os.path.realpath(__file__))
            executables = ["ffmpeg.exe", "ffprobe.exe", "ffplay.exe"]
            
            for exe in executables:
                exe_path = next(Path(extract_path).rglob(exe))
                new_exe_path = os.path.join(script_dir, exe)
                shutil.move(str(exe_path), new_exe_path)

            # Clean up
            os.remove(zip_path)
            shutil.rmtree(extract_path)

            print("FFmpeg installation complete.")
            messagebox.showinfo("FFmpeg Installed", "FFmpeg has been successfully downloaded and installed.")

            return os.path.join(script_dir, "ffmpeg.exe")
        except Exception as e:
            error_msg = f"Error downloading FFmpeg: {e}"
            print(error_msg)
            messagebox.showerror("FFmpeg Download Error", error_msg)
            return None

    def get_ffmpeg_path(self):
        executables = ["ffmpeg", "ffprobe", "ffplay"]
        
        # Check if executables are in PATH
        if all(shutil.which(exe) for exe in executables):
            return "ffmpeg"

        # Check if executables are in the same directory as the script
        script_dir = os.path.dirname(os.path.realpath(__file__))
        if all(os.path.exists(os.path.join(script_dir, f"{exe}.exe")) for exe in executables):
            return os.path.join(script_dir, "ffmpeg.exe")

        return None

class SongBrowser(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Song Browser")
        self.geometry("800x600")
        
        # Make the window appear on top
        self.lift()
        self.attributes('-topmost', True)
        
        self.songs = []
        self.current_song = None
        self.audio_data = None
        self.is_playing = False
        self.selected_index = None
        
        self.create_widgets()
        self.fetch_songs()
        
        pygame.mixer.init()
        
        # Schedule removing topmost attribute
        self._after_id = self.after(100, self.remove_topmost)

    def remove_topmost(self):
        self.attributes('-topmost', False)

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Headers
        self.artist_header = ctk.CTkLabel(self.main_frame, text="Artist", font=("Arial", 16, "bold"))
        self.artist_header.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.title_header = ctk.CTkLabel(self.main_frame, text="Title", font=("Arial", 16, "bold"))
        self.title_header.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # Scrollable frames for artists and titles
        self.artist_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.artist_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.title_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.title_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Control frame
        self.control_frame = ctk.CTkFrame(self.main_frame)
        self.control_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.control_frame.grid_columnconfigure(2, weight=1)

        self.play_button = ctk.CTkButton(self.control_frame, text="Play", width=100, command=self.play_song)
        self.play_button.grid(row=0, column=0, padx=5, pady=5)

        self.stop_button = ctk.CTkButton(self.control_frame, text="Stop", width=100, command=self.stop_song)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)

        # Now playing label
        self.now_playing_label = ctk.CTkLabel(self.control_frame, text="", font=("Arial", 14))
        self.now_playing_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")

    def fetch_songs(self):
        try:
            response = requests.get('https://www.komplexaci.cz/music/')
            soup = BeautifulSoup(response.text, 'html.parser')
            
            ogg_files = [link.get('href') for link in soup.find_all('a') if link.get('href', '').endswith('.ogg')]
            
            for i, file in enumerate(ogg_files):
                url = f"https://www.komplexaci.cz/music/{file}"
                artist, title = self.parse_filename(file)
                self.songs.append({"url": url, "artist": artist, "title": title})
                
                artist_label = ctk.CTkLabel(self.artist_frame, text=artist, font=("Arial", 12), anchor="w")
                artist_label.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
                
                title_label = ctk.CTkLabel(self.title_frame, text=title, font=("Arial", 12), anchor="w")
                title_label.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
                
                artist_label.bind("<Button-1>", lambda e, idx=i: self.select_song(idx))
                title_label.bind("<Button-1>", lambda e, idx=i: self.select_song(idx))
        except Exception as e:
            print(f"Error fetching songs: {e}")

    def parse_filename(self, filename):
        name = urllib.parse.unquote(filename[:-4])
        parts = name.split('-')
        if len(parts) >= 2:
            return parts[0].strip(), '-'.join(parts[1:]).strip()
        return name, ""

    def select_song(self, index):
        if self.selected_index is not None:
            self.artist_frame.winfo_children()[self.selected_index].configure(fg_color=("gray86", "gray17"))
            self.title_frame.winfo_children()[self.selected_index].configure(fg_color=("gray86", "gray17"))
        
        self.selected_index = index
        self.current_song = self.songs[index]
        self.artist_frame.winfo_children()[index].configure(fg_color=("gray76", "gray27"))
        self.title_frame.winfo_children()[index].configure(fg_color=("gray76", "gray27"))
        self.now_playing_label.configure(text=f"Selected: {self.current_song['artist']} - {self.current_song['title']}")

    def play_song(self):
        if self.current_song:
            self.stop_song()
            self.is_playing = True
            threading.Thread(target=self._download_and_play, args=(self.current_song["url"],), daemon=True).start()
            self.now_playing_label.configure(text=f"Now Playing: {self.current_song['artist']} - {self.current_song['title']}")

    def _download_and_play(self, url):
        try:
            response = requests.get(url)
            self.audio_data = BytesIO(response.content)
            
            pygame.mixer.music.load(self.audio_data)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error playing song: {e}")

    def stop_song(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self.audio_data = None
        self.is_playing = False
        self.now_playing_label.configure(text="")

    def on_closing(self):
        self.stop_song()
        self.destroy()

if __name__ == "__main__":
    app = AudioConverterApp()
    app.mainloop()