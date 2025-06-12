def sum_command(user_text):
    """Maneja el comando de suma, extrayendo números de la frase."""
    numbers = re.findall(r'\d+\.?\d*', user_text)
    
    if len(numbers) >= 2:
        try:
            num1 = float(numbers[0])
            num2 = float(numbers[1])
            result = num1 + num2
            AssistantResponse(f'La suma de {num1} más {num2} es {result}')
        except ValueError:
            AssistantResponse("Lo siento, no pude entender los números para la suma.")
        except Exception as e:
            AssistantResponse(f"Ocurrió un error al intentar sumar: {e}")
    else:
        AssistantResponse("Para la suma, necesito al menos dos números. Por favor, dímelos.")