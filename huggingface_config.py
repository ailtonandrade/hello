# huggingface_config.py - AUTO-GERADO
import os

E_DRIVE = "E:\\HuggingFace"
PATHS = {'HF_HOME': 'E:\\HuggingFace\\models', 'HF_DATASETS_CACHE': 'E:\\HuggingFace\\cache\\datasets', 'HF_MODULES_CACHE': 'E:\\HuggingFace\\cache\\modules', 'TRANSFORMERS_CACHE': 'E:\\HuggingFace\\models\\transformers', 'DIFFUSERS_CACHE': 'E:\\HuggingFace\\models\\diffusers'}

for key, path in PATHS.items():
    os.environ[key] = path
    os.makedirs(path, exist_ok=True)

print(f"✅ Cache configurado: {E_DRIVE}")
