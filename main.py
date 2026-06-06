import os
import json
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List

# Konfigurasi API Key Gemini
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
genai.configure(api_key=API_KEY)

# Definisi struktur data Test Case menggunakan Pydantic
class TestCase(BaseModel):
    test_case_id: str = Field(description="Unique ID for the test case, e.g., TC001")
    scenario: str = Field(description="The description of what is being tested")
    test_steps: str = Field(description="Step by step instructions to execute the test")
    expected_result: str = Field(description="The expected successful outcome")
    test_type: str = Field(description="Positive or Negative")

class TestCaseList(BaseModel):
    suite_name: str
    cases: List[TestCase]

def generate_test_cases(feature_description: str) -> str:
    """
    Menggunakan Gemini LLM untuk menganalisis fitur dan menghasilkan skenario pengujian.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert QA Automation Engineer. Analyze the following feature description 
    and generate a comprehensive list of test cases including both positive and negative scenarios.
    
    Feature Description:
    {feature_description}
    """
    
    # Memaksa output berupa JSON terstruktur sesuai skema Pydantic
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=TestCaseList
        )
    )
    return response.text

def export_to_sheets_format(json_data: str):
    """
    Simulasi pemrosesan data sebelum dikirimkan ke komponen Google Sheets di Langflow
    """
    data = json.loads(json_data)
    print(f"Exporting Test Suite: {data['suite_name']}\n")
    
    # Headers untuk Google Sheets
    headers = ["Test Case ID", "Scenario", "Test Steps", "Expected Result", "Type"]
    print(f"{' | '.join(headers)}")
    print("-" * 80)
    
    for case in data['cases']:
        print(f"{case['test_case_id']} | {case['scenario']} | {case['test_steps']} | {case['expected_result']} | {case['test_type']}")

if __name__ == "__main__":
    # Contoh input penjelasan fitur dari chat
    user_feature_input = """
    Fitur ganti kata sandi (Change Password) pada aplikasi. 
    Syarat: Kata sandi lama harus benar, kata sandi baru minimal 8 karakter, 
    harus mengandung kombinasi angka dan huruf kapital, serta konfirmasi kata sandi baru harus cocok.
    """
    
    print("Menganalisis fitur dan membuat Test Case via AI...")
    raw_output = generate_test_cases(user_feature_input)
    export_to_sheets_format(raw_output)