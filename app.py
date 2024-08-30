import os
import subprocess
import logging
import requests

class InferlessPythonModel:
    def initialize(self):
        subprocess.run(["wget", "https://github.com/rbgo404/Files/raw/main/build.sh"])
        subprocess.run(["bash", "build.sh"], check=True)

    def infer(self, inputs):
        return {"status":"GOOD"}

    def finalize(self):
      pass
