from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import socket
import threading # Donmayi engellemek icin arka plan destegi

# Pencere arka plan rengini modern bir koyu gri yapıyoruz
Window.clearcolor = (0.07, 0.08, 0.09, 1)
# İlk açılış pencere boyutunu ayarlayalım
Window.size = (500, 450)

# Sunucuların Bilgileri
Server_List = {
    "Berke Sunucu": ("25.38.216.250", 25565),
    "Erdem Sunucu": ("25.36.120.122", 25565),
    "Eray Sunucu": ("25.25.252.165", 25565)
}

class ServerCheckApp(App):
    def build(self):
        self.title = "Minecraft Server Online-Offline Durumu"
        
        # Ana dikey düzen
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # Başlık Bölümü
        self.layout.add_widget(Label(
            text="Minecraft Sunucu Durumları", 
            font_size=22, 
            bold=True,
            color=(0.9, 0.9, 0.95, 1),
            size_hint_y=None,
            height=50
        ))
        
        # Sunucu listesi için dikey kutu
        self.server_list_layout = BoxLayout(orientation='vertical', spacing=20)
        
        self.labels = {}
        for isim, (ip, port) in Server_List.items():
            # Her sunucu için yatay bir satır
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=55)
            
            # İsim ve IP adresini alt alta göstermek için dikey bir iç kutu
            text_box = BoxLayout(orientation='vertical')
            
            isim_label = Label(
                text=isim, 
                font_size=16, 
                bold=True,
                halign='left', 
                valign='middle',
                color=(0.85, 0.85, 0.85, 1)
            )
            isim_label.bind(size=isim_label.setter('text_size'))
            
            ip_label = Label(
                text=f"[{ip}]", 
                font_size=13, 
                halign='left', 
                valign='middle',
                color=(0.5, 0.55, 0.6, 1) # IP adresini biraz daha sönük estetik bir renk yaptık
            )
            ip_label.bind(size=ip_label.setter('text_size'))
            
            text_box.add_widget(isim_label)
            text_box.add_widget(ip_label)
            
            # Durum etiketi (Sağa dayalı)
            durum_label = Label(
                text="[ KONTROL EDILIYOR ]", 
                font_size=15, 
                bold=True,
                halign='right', 
                valign='middle',
                color=(0.9, 0.7, 0.1, 1)
            )
            durum_label.bind(size=durum_label.setter('text_size'))
            
            row.add_widget(text_box)
            row.add_widget(durum_label)
            self.server_list_layout.add_widget(row)
            
            self.labels[isim] = durum_label
            
        self.layout.add_widget(self.server_list_layout)
        
        # Şık, genişliği sınırlı modern buton
        self.refresh_btn = Button(
            text="Simdi Yenile",
            size_hint=(None, None),
            size=(180, 50),
            pos_hint={'center_x': 0.5},
            background_color=(0.12, 0.53, 0.9, 1), # Canlı modern mavi
            background_normal='',                 # Varsayılan eski gri dokuyu siler
            font_size=15,
            bold=True
        )
        self.refresh_btn.bind(on_press=self.kontrolu_baslat)
        self.layout.add_widget(self.refresh_btn)
        
        # İlk durum kontrolünü yap
        self.kontrolu_baslat()
        
        # Her 30 saniyede bir otomatik yenile
        Clock.schedule_interval(self.kontrolu_baslat, 30)
        
        return self.layout

    def sunucu_acik_mi(self, ip, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0) # Zaman aşımını optimize ettik
            s.connect((ip, port))
            s.close()
            return True
        except:
            return False

    def kontrolu_baslat(self, *args):
        # Arayüzün kilitlenmemesi için kontrolü arka planda çalıştırıyoruz
        threading.Thread(target=self.durumlari_guncelle, daemon=True).start()

    def durumlari_guncelle(self):
        # Önce durum yazılarını "Kontrol Ediliyor..." yapalım
        for isim in Server_List.keys():
            def yaziyi_guncelle(dt, name=isim):
                self.labels[name].text = "[ KONTROL EDILIYOR... ]"
                self.labels[name].color = (0.9, 0.7, 0.1, 1)
            Clock.schedule_once(yaziyi_guncelle)

        # Arka planda sunucuları tara ve sonuçları yansıt
        for isim, (ip, port) in Server_List.items():
            if self.sunucu_acik_mi(ip, port):
                def aktif_yap(dt, name=isim):
                    self.labels[name].text = "[ AKTIF ]"
                    self.labels[name].color = (0.25, 0.75, 0.35, 1) # Tatlı bir yeşil
                Clock.schedule_once(aktif_yap)
            else:
                def kapali_yap(dt, name=isim):
                    self.labels[name].text = "[ KAPALI ]"
                    self.labels[name].color = (0.85, 0.25, 0.25, 1) # Yumuşak bir kırmızı
                Clock.schedule_once(kapali_yap)

if __name__ == '__main__':
    ServerCheckApp().run()