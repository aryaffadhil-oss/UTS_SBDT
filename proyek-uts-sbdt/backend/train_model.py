import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

iris = load_iris()
X, y = iris.data, iris.target

model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X, y)

joblib.dump({"model": model, "target_names": iris.target_names.tolist()}, "model.joblib")
print("Model berhasil disimpan ke model.joblib")