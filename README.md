# QTHACK_qkms
Quantum Key Management System(QKMS)-QTHACK2020

## Özet
E91 anahtar dağıtımı kullanarak, uçtan uca güvenli iletişim sağlayan sistem. Sunucu tarafından sağlanan EPR çiftleri, 128 bitlik bir anahtar oluşturmak için kullanılıyor. Daha sonra bu anahtar kullanılarak mesajlarımız AES128 kullanarak simetrik bir şekilde şifreleniyor. Bu sistem üzerine bir mesajlaşma arayüzü de yazdık. Simulaqron kullanılarak simüle edildi.

## Açıklama
Mesaj yollamak isteyen kullanıcı, sunucu ile iletişime geçerek EPR çiftlerinin dağıtılmasını istiyor. Sunucu iki kullanıcıya da EPR çifti gönderiyor. Kullanıcılar bu EPR çiftlerini kullanarak kendi aralarında klasik kanal kullanarak bir anahtar elde ediyorlar. Bu anahtar uzunluğu 128 bit'e ulaşana kadar bu işlem tekrar ediyor. Daha sonrasında kullanıcılar mesajlarını AES128 kullanrak şifreleyerek birbirlerine gönderebiliyorlar. Şifrelerin kontrolü için ise SHA256 ile hash'lenmiş şifreler karşılaştırılıyor. Bu durum olası gürültü veya dinleyen birisi olması durumunda koruma sağlıyor. Bozulmuş bir şifre bulunması durumunda yeni bir şifre oluşturuluyor.

## Takım Üyeleri
@barancengiz | İsim: Baran Cengiz
@kanspretsa | İsim: Kadircan Becek
@ | İsim: Tansu Demerci
@ | İsim: Güneş Karaalp


## Kullanım

Simulaqron indirmek için (Linux):
```
pip3 install simulaqron
```

Test etmek için terminalden python3 yazdıktan sonra unittest'i deneyebilirsiniz.
```
import simulaqron
simulaqron.tests()
```

Simulaqron'u başlatın
```
simulaqron start
```
Kullanıcı 'node'larını oluşturun. Her kullanıcı, veri alma ve yollama işleri için ayrı bir socket kullanmakta. Aşağıdaki yöntemle 2 node oluşturabilirsiniz.
```
simulaqron --nodes Node1s,Node1r,Node2s,Node2r,Server
```
Simulaqron default network değiştermek istiyor musunuz diye soracak. yes yazın. Eğer sormamışsa bir sıkıntı var demektir, simulaqronu durdurun ve baştan başlatın.
```
simulaqron stop
simulaqron reset
```
Sunucuyu başlatın
```
python3 test_server.py
```
Grafik kullanıcı arayüzlerini başlatın. Aşağıdaki kodu her bir kullanıcı için bir kere çalıştırın. 
```
python3 GUI.py
```
Source kısmına şimdiki kullanıcıyı, dest kısmına konuşmak istediğiniz kullanıcıyı girin. Node1 için sadece 1, Node2 için sadece 2 yazın. Aksi durumda node'lar bulunamayak ve kod hata verecektir.

Açılan pencerede mesajını yazın ve "Send"e tıklayın. (Göndermek için Enter tuşu çalışmamaktadır)
İlk mesajın gönderilmesi bir miktar zaman alacaktır. Bu süreçte kullanıcılar sunucuyla iletişim kurarak anahtarlar oluşturmaktadır. Sonraki mesajlar ise anında yollanacaktır.

Tebrikler

### Gelecek İşler: Sistemin simülasyon dışında da çalışabilmesi için E91 paylaşımı içerisinde hata doğrulama algoritmaları kullanılmalıdır. Gönderimde oluşacak hataların düzeltilmesi ve dinlenme sonucu oluşacak hataların düzeltilmesi gereklidir. Simülasyon programları qubit sayısını sınırladığından ve kuantum işlemleri simülasyonda çok yavaş yapıldığından, şimdilik sisteme böyle bir algoritma eklenmemiştir.
