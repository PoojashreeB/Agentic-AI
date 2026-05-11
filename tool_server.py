from flask import Flask, request, jsonify
import ast
import operator

app = Flask(__name__)

def calculate(expression: str) -> str:
    ops = {
        ast.Add:  operator.add,
        ast.Sub:  operator.sub,
        ast.Mult: operator.mul,
        ast.Div:  operator.truediv,
        ast.Pow:  operator.pow,
        ast.USub: operator.neg,
    }
    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](_eval(node.operand))
    try:
        tree = ast.parse(expression, mode="eval")
        return str(round(_eval(tree.body), 6))
    except Exception as e:
        return f"Error: {e}"

@app.route("/calculate", methods=["POST"])
def calculate_endpoint():
    data = request.json
    expression = data.get("expression", "")
    result = calculate(expression)
    return jsonify({"result": result})

@app.route("/", methods=["GET"])
def home():
    return "Tool server is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
