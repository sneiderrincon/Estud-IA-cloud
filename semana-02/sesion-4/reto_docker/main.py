from fastapi import FastAPI
import torch

app = FastAPI(title="reto-docker")


def create_tensors(shape: tuple[int, int] = (2, 3)) -> dict:
    rand_tensor = torch.rand(shape)
    ones_tensor = torch.ones(shape)
    zeros_tensor = torch.zeros(shape)

    print(f"Random Tensor: \n {rand_tensor} \n")
    print(f"Ones Tensor: \n {ones_tensor} \n")
    print(f"Zeros Tensor: \n {zeros_tensor}")

    return {
        "shape": list(shape),
        "rand_tensor": rand_tensor.tolist(),
        "ones_tensor": ones_tensor.tolist(),
        "zeros_tensor": zeros_tensor.tolist(),
    }


@app.get("/")
def root():
    return {"message": "Hello from reto-docker!"}


@app.get("/tensors")
def tensors():
    return create_tensors()


def main():
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
