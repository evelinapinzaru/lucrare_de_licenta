# CodeFlow - aplicație web educațională pentru învățarea programării prin exerciții personalizate

## Detalii legate de repository:

Adresa repository-ului: [https://gitlab.upt.ro/evelina.pinzaru/lucrare_de_licenta.git](https://gitlab.upt.ro/evelina.pinzaru/lucrare_de_licenta.git).  

Repository-ul **lucrare_de_licență** are următoarea structură:
- directorul **aplicatie_web**  --> aici se află codul sursă al aplicației
- **.gitattributes**
- **.gitignore** 
- **LICENSE**
- **README.md**
- **launch.py** --> script de rulare unificată a aplicației

Directorul **aplicatie_web** are următoarea structură:
- **backend** --> codul sursă pentru partea de backend
- **frontend** --> codul sursă pentru partea de frontend

---

## Pași pentru lansarea aplicației:

1. Clonarea repository-ului
```bash
git clone https://gitlab.upt.ro/evelina.pinzaru/lucrare_de_licenta.git
cd lucrare_de_licenta
```

2. Din directorul **backend** se intalează dependințele astfel:
```bash
cd backend
pip install -r requirements.txt
```

3. Din directorul **frontend** se intalează dependințele astfel:
```bash
cd ../frontend
pnpm install
```

4. Lansarea aplicației se face din directorul **lucrare_de_licenta** cu ajutorul comenzii:
```bash
cd ..
python launch.py
```