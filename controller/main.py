from bpsky import bpsky
from controller.utils import *


@bpsky.route("/", methods=["GET"])
def root():
    return redirect("/api/v1/")


@bpsky.route("/api/v1/", methods=["GET"])
def main():
    return "Welcome to BPSky"
