from pydantic import BaseModel, Field


class ChavePixBase(BaseModel):
    chave_pix: str = Field(description="Chave pix.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "chave_pix": "00020101021226850014br.gov.bcb.pix2563qrcodepix.example.com/pix/v2/exemplo-1234-5678-90ab-cdefghijklmn5204000053039865802BR5913LOJA EXEMPLO6008CIDADE X62070503***6304A1B2"
                }
            ]
        }
    }
