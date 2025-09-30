from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(creds)


spreadsheet_id = "1D-rEgREaINRX-Jr5RY60yfZVau0zVaTF_JnyLLevp24"


sheet = client.open_by_key(spreadsheet_id).sheet1

spreadsheet_id_second = "1eZUd2oNxvm7nikfzDeT4mr5dDculuBDAviwNbl5rvX0"


sheet_second = client.open_by_key(spreadsheet_id_second).sheet1



@app.get("/")
def home():
    return {"message": "Backend API is running"}



from fastapi import HTTPException
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/login")
def login(data: LoginRequest):
 
    if data.username == "admin" and data.password == "password123":
        return {"success": True, "message": "Login berhasil"}
    else:
        raise HTTPException(status_code=401, detail="Username atau password salah")


@app.post("/api/logout")
def logout():

    return {"success": True, "message": "Logout berhasil"}


@app.get("/api/data")
def get_data():
    records = sheet.get_all_records()  
    
    processed = []
    for row in records:
        try:
           
            kbhj_date = datetime.strptime(row["KBJH_DATE"], "%d-%b-%y")

            
            shipment_id = row["KBJDO_SHIPMENT_ID"]
            shipment_date_str = shipment_id.split("-")[1]

       
            if shipment_id.startswith("RS"):
                shipment_date = datetime.strptime(shipment_date_str, "%d%m%y")
            else:
                shipment_date = datetime.strptime(shipment_date_str, "%y%m%d")


            row["tgl shipment"] = shipment_date.strftime("%d-%b-%y")

     
            lama_hari = (kbhj_date - shipment_date).days
            row["lama hari"] = lama_hari
        except Exception as e:
            row["tgl shipment"] = None
            row["lama hari"] = None
        
        processed.append(row)
    
    return {"data": processed}

@app.get("/api/data2")
def get_data2():
    try:
        records = sheet_second.get_all_records()

        grouped = {}

        for idx, row in enumerate(records, start=1):
            giro = row.get("NCTR_NO_GIRO")
            if not giro:
                continue

            if giro not in grouped:
                grouped[giro] = {
                    "header": {
                        "OA": row.get("BKARH_DATE"),
                        "REKENING": row.get("NCTR_MSB_CODE"),
                        "No_Giro": giro
                    },
                    "data": [],
                    "TOTAL": 0
                }


            msb_code = str(row.get("NCTR_MSB_CODE", "")).upper()
            if msb_code.startswith("PS"):
                nama_bank = "BCA"
            elif msb_code.startswith("PM"):
                nama_bank = "MANDIRI"
            else:
                nama_bank = msb_code if msb_code else "-"

            item = {
                "No": len(grouped[giro]["data"]) + 1,
                "Nama Produk": row.get("DIBAYAR_KPD"),
                "Nama Perusahaan": row.get("NAMA_PERUSAHAAN"),
                "No Rekening": row.get("NCTR_REK_NO"),
                "Nama Bank": nama_bank,
                "Nomor OA": row.get("BKARH_NO"),
                "Jml Transfer Vendor": row.get("JML_TRANSFER_VENDOR"),
                "Pengurangan/Penambahan": row.get("PENAMBAHAN_PENGURANGAN"),
                "Total Bayar": row.get("OA_AMOUNT"),
                "Keterangan": row.get("KETERANGAN")
            }

            oa_amount_raw = str(row.get("OA_AMOUNT") or "0")
            try:
                # Hilangkan titik ribuan, lalu coba float (untuk notasi ilmiah)
                oa_amount_clean = oa_amount_raw.replace(".", "")
                total_value = int(float(oa_amount_clean))
            except ValueError:
                total_value = 0
            grouped[giro]["TOTAL"] += total_value
            grouped[giro]["data"].append(item)

        return {"groups": list(grouped.values())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membaca sheet kedua: {e}")


handler = Mangum(app)