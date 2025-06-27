from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel, Field,computed_field 
from typing import Annotated,Literal,Optional  

class Patient(BaseModel):
    id:Annotated[str,Field(...,description="Id of patient",example="P001")]
    name:Annotated[str,Field(...,description="Name of patient")]
    city:Annotated[str,Field(...,description="City of patient")]
    age:Annotated[int,Field(...,description="Age",gt=0,lt=120)]
    gender:Annotated[Literal['male','female','other'],Field(...,description="Gender of patient")]
    height:Annotated[float,Field(...,gt=0,description="Height of patient in m")]
    weight:Annotated[float,Field(...,gt=0,description="Weight of patient in kg")]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"



class UpdatePatient(BaseModel):
    
    name:Annotated[Optional[str],Field(default=None)]
    city:Annotated[Optional[str],Field(default=None)]
    age:Annotated[Optional[int],Field(default=None,description="Age",gt=0,lt=120)]
    gender:Annotated[Optional[Literal['male','female','other']],Field(default=None,description="Gender of patient")]
    height:Annotated[Optional[float],Field(default=None,gt=0,description="Height of patient in m")]
    weight:Annotated[Optional[float],Field(default=None,gt=0,description="Weight of patient in kg")]

def load_data():
    with open('patients.json','r') as f:
        data=json.load(f)

    return data  

def save_data(data):
   with open("patients.json",'w') as f:
       json.dump(data,f)  


app=FastAPI()

@app.get("/")
def hello():
    return{'message': 'Patient Management System'}

@app.get('/about')
def about():
    return {'message': 'This is a patient management system using FastAPI. It allows you to update, view, delete, and add patients.'}

@app.get('/view')
def view():
    data=load_data()
    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id:str=Path(...,Description="The ID of patient in DB",example="P002")):
    data=load_data()
    if patient_id in data:
        return data[patient_id]
    else:
        #return("ERROR:Patient not found") json response
        raise HTTPException(status_code=404, detail="Patient not found")



@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')):
    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order select between asc and desc')
    
    data = load_data()

    sort_order = True if order=='desc' else False

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)
    return sorted_data

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    
    data[patient.id] = patient.model_dump(exclude=['id'])
    save_data(data)
    return JSONResponse(status_code=201, content={"message": "Patient created successfully"})


@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: UpdatePatient):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    existing_info = data[patient_id]
    updated_info = patient_update.model_dump(exclude_unset=True)

    for key,value in updated_info.items():
        updated_info[key]=value

    data[]    
    