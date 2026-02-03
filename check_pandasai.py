import pandasai
print(f"PandasAI Path: {pandasai.__file__}")
try:
    from pandasai import SmartDataframe
    print("Success: from pandasai import SmartDataframe")
except ImportError:
    print("Failed: from pandasai import SmartDataframe")

try:
    from pandasai.smart_dataframe import SmartDataframe
    print("Success: from pandasai.smart_dataframe import SmartDataframe")
except ImportError:
    print("Failed: from pandasai.smart_dataframe import SmartDataframe")

print("Dir(pandasai):", dir(pandasai))
