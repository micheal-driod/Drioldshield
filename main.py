%%writefile main.py
import socket
import threading
import time
from datetime import datetime

# Kivy Imports
from kivy.app import App
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import platform

# --- CONFIG ---
CYBER_GREEN = (0, 1, 0.4, 1)
ALERT_RED = (1, 0, 0, 1)
DARK_BG = (0.05, 0.05, 0.05, 1)
store = JsonStore('secure_data.json')

# --- UNIVERSAL AUDIO ENGINE ---
class AudioEngine:
    def __init__(self):
        self.is_android = platform == 'android'
        self.rec = None; self.track = None
        self.pa = None; self.stream_in = None; self.stream_out = None
        self.rate = 16000; self.chunk = 1024
        
        if self.is_android:
            try:
                from jnius import autoclass
                self.AudioRecord = autoclass('android.media.AudioRecord')
                self.AudioTrack = autoclass('android.media.AudioTrack')
                self.AudioFormat = autoclass('android.media.AudioFormat')
                self.MediaRecorder = autoclass('android.media.MediaRecorder$AudioSource')
                self.AudioManager = autoclass('android.media.AudioManager')
                self.channel_in = self.AudioFormat.CHANNEL_IN_MONO
                self.channel_out = self.AudioFormat.CHANNEL_OUT_MONO
                self.encoding = self.AudioFormat.ENCODING_PCM_16BIT
                self.buf_rec = self.AudioRecord.getMinBufferSize(self.rate, self.channel_in, self.encoding) * 2
                self.buf_play = self.AudioTrack.getMinBufferSize(self.rate, self.channel_out, self.encoding) * 2
            except: pass
        else:
            try:
                import pyaudio
                self.pa = pyaudio.PyAudio()
            except: pass

    def start(self):
        if self.is_android:
            try:
                self.rec = self.AudioRecord(self.MediaRecorder.MIC, self.rate, self.channel_in, self.encoding, self.buf_rec)
                self.track = self.AudioTrack(self.AudioManager.STREAM_MUSIC, self.rate, self.channel_out, self.encoding, self.buf_play, self.AudioTrack.MODE_STREAM)
                self.rec.startRecording(); self.track.play()
                return True
            except: return False
        elif self.pa:
            self.stream_in = self.pa.open(format=self.pa.get_format_from_width(2), channels=1, rate=self.rate, input=True, frames_per_buffer=self.chunk)
            self.stream_out = self.pa.open(format=self.pa.get_format_from_width(2), channels=1, rate=self.rate, output=True)
            return True
        return False

    def read(self):
        if self.is_android and self.rec:
            b = bytearray(self.chunk)
            r = self.rec.read(b, 0, self.chunk)
            if r > 0: return bytes(b[:r])
        elif self.stream_in: return self.stream_in.read(self.chunk, exception_on_overflow=False)
        return None

    def write(self, data):
        if self.is_android and self.track: self.track.write(data, 0, len(data))
        elif self.stream_out: self.stream_out.write(data)

    def stop(self):
        try:
            if self.is_android: self.rec.stop(); self.track.stop()
            elif self.pa: self.stream_in.stop_stream(); self.stream_out.stop_stream()
        except: pass

audio = AudioEngine()

# --- UTILS ---
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]; s.close(); return ip
    except: return "127.0.0.1"

# --- SCREENS ---
class Dashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="[ DROID SHIELD ]", font_size='30sp', color=CYBER_GREEN, size_hint=(1, 0.15)))
        layout.add_widget(Label(text=f"ID: {get_ip()}", color=(0.5,0.5,0.5,1), size_hint=(1, 0.05)))
        
        grid = GridLayout(cols=2, spacing=15, size_hint=(1, 0.6))
        btns = [("PASS AUDIT", self.pass_check), ("IP SCAN", self.ip_check),
                ("GLOBAL LINK", self.connect_server), ("VAULT", self.vault), 
                ("LOGS", self.view_logs)]
        
        for t, f in btns:
            b = Button(text=t, background_color=(0, 0.3, 0.1, 1), color=CYBER_GREEN, bold=True)
            b.bind(on_press=f)
            grid.add_widget(b)
        layout.add_widget(grid)
        self.add_widget(layout)

    def pass_check(self, i):
        c = BoxLayout(orientation='vertical', spacing=10)
        inp = TextInput(hint_text="Password"); l = Label(text="...")
        def check(x): l.text = "STRONG" if len(inp.text) > 8 else "WEAK"
        b = Button(text="CHECK", background_color=CYBER_GREEN); b.bind(on_press=check)
        c.add_widget(inp); c.add_widget(b); c.add_widget(l)
        Popup(title="AUDIT", content=c, size_hint=(0.8, 0.4)).open()

    def ip_check(self, i):
        c = BoxLayout(orientation='vertical'); l = Label(text=f"IP: {get_ip()}\nStatus: EXPOSED")
        c.add_widget(l); Popup(title="IP SCAN", content=c, size_hint=(0.8, 0.3)).open()

    def vault(self, i):
        c = BoxLayout(orientation='vertical')
        t = TextInput(text=store.get('vault')['data'] if store.exists('vault') else "")
        def s(x): store.put('vault', data=t.text)
        b = Button(text="SAVE", background_color=CYBER_GREEN); b.bind(on_press=s)
        c.add_widget(t); c.add_widget(b); Popup(title="VAULT", content=c, size_hint=(0.9, 0.6)).open()

    def view_logs(self, i):
        Popup(title="LOGS", content=Label(text="System Secure."), size_hint=(0.8, 0.4)).open()

    def connect_server(self, i):
        c = BoxLayout(orientation='vertical', spacing=10)
        ip = TextInput(hint_text="Server IP (e.g., 192.168.1.5)", multiline=False)
        usr = TextInput(hint_text="Username", multiline=False)
        btn = Button(text="INITIATE UPLINK", background_color=CYBER_GREEN)
        p = Popup(title="SATELLITE CONNECTION", content=c, size_hint=(0.9, 0.5))
        
        def start(x):
            if ip.text and usr.text:
                p.dismiss()
                App.get_running_app().launch_comms(ip.text, usr.text)
        btn.bind(on_press=start)
        c.add_widget(ip); c.add_widget(usr); c.add_widget(btn); p.open()

class CommsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10)
        self.header = Label(text="CONNECTING...", size_hint=(1, 0.1), color=CYBER_GREEN)
        self.output = TextInput(readonly=True, background_color=DARK_BG, foreground_color=CYBER_GREEN)
        self.input_box = BoxLayout(size_hint=(1, 0.15))
        self.msg_in = TextInput(hint_text="Type Message..."); self.send_btn = Button(text="SEND", size_hint=(0.3, 1))
        self.input_box.add_widget(self.msg_in); self.input_box.add_widget(self.send_btn)
        self.btn_mic = Button(text="MIC OFF", background_color=ALERT_RED, size_hint=(1, 0.15))
        
        self.layout.add_widget(self.header); self.layout.add_widget(self.output)
        self.layout.add_widget(self.input_box); self.layout.add_widget(self.btn_mic)
        
        btn_exit = Button(text="DISCONNECT", size_hint=(1, 0.1), background_color=(0.5,0,0,1))
        btn_exit.bind(on_press=self.disconnect)
        self.layout.add_widget(btn_exit)
        self.add_widget(self.layout)
        
        self.active = False
        self.mic_active = False

    def start(self, server_ip, username):
        self.server_ip = server_ip; self.username = username; self.active = True
        self.header.text = f"CONNECTED TO: {server_ip}"
        self.log(f"--- UPLINK ESTABLISHED AS {username} ---")
        
        # Sockets
        try:
            self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp.connect((server_ip, 8888))
            self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Start Threads
            threading.Thread(target=self.listen_tcp, daemon=True).start()
            threading.Thread(target=self.listen_udp, daemon=True).start()
            
            # Bind Buttons
            self.send_btn.bind(on_press=self.send_msg)
            self.btn_mic.bind(on_press=self.toggle_mic)
            audio.start()
            
        except Exception as e:
            self.log(f"CONNECTION FAILED: {e}")

    def listen_tcp(self):
        while self.active:
            try:
                data = self.tcp.recv(1024)
                if data: self.log(data.decode('utf-8'))
            except: break

    def listen_udp(self):
        # Send initial packet to register with server
        self.udp.sendto(b'PING', (self.server_ip, 9999))
        while self.active:
            try:
                data, _ = self.udp.recvfrom(4096)
                audio.write(data)
            except: pass

    def send_audio(self):
        while self.active and self.mic_active:
            data = audio.read()
            if data:
                try: self.udp.sendto(data, (self.server_ip, 9999))
                except: pass

    def toggle_mic(self, i):
        self.mic_active = not self.mic_active
        if self.mic_active:
            self.btn_mic.text = "MIC LIVE (Transmitting)"
            self.btn_mic.background_color = CYBER_GREEN
            threading.Thread(target=self.send_audio, daemon=True).start()
        else:
            self.btn_mic.text = "MIC OFF"
            self.btn_mic.background_color = ALERT_RED

    def send_msg(self, i):
        if self.msg_in.text:
            msg = f"{self.username}: {self.msg_in.text}"
            try: self.tcp.send(msg.encode('utf-8')); self.log(f"ME: {self.msg_in.text}"); self.msg_in.text = ""
            except: pass

    def log(self, txt): Clock.schedule_once(lambda dt: setattr(self.output, 'text', self.output.text + "\n" + txt))
    
    def disconnect(self, i):
        self.active = False; audio.stop()
        try: self.tcp.close(); self.udp.close()
        except: pass
        App.get_running_app().sm.current = 'dash'

class DroidShieldApp(App):
    def build(self):
        Window.clearcolor = DARK_BG
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.INTERNET, Permission.RECORD_AUDIO, Permission.MODIFY_AUDIO_SETTINGS])
        self.sm = ScreenManager()
        self.sm.add_widget(Dashboard(name='dash'))
        self.sm.add_widget(CommsScreen(name='comms'))
        return self.sm
    def launch_comms(self, ip, usr):
        s = self.sm.get_screen('comms'); s.start(ip, usr); self.sm.current = 'comms'

if __name__ == '__main__': DroidShieldApp().run()