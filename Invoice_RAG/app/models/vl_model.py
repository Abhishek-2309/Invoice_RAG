from unsloth import FastVisionModel
import torch

def load_model():
    model, tokenizer = FastVisionModel.from_pretrained(
        "unsloth/Qwen2.5-VL-7B-Instruct",
        load_in_4bit=True,
        use_gradient_checkpointing="unsloth",
    )
    FastVisionModel.for_inference(model)
    return model, tokenizer

def run_answer(model, tokenizer, question: str, image):
    prompt = f"""Answer the question based on the following image. Give your final answer strictly in a json schema with the same key asked in question.
Question: {question}"""
    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt}]}]
    input_text = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
    inputs = tokenizer(image, input_text, add_special_tokens=False, return_tensors="pt").to("cuda")
    with torch.inference_mode():
        outputs = model.generate(**inputs, max_new_tokens=512, use_cache=True)
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    del inputs, outputs
    torch.cuda.empty_cache()
    return decoded
