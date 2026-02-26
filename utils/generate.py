def generate_module_id():
    for i in range(1, 10000):
        id = "M" + str(i).zfill(2) + "_"
        yield id

def generate_case_id():
    for i in range(1, 10000):
        id = "C" + str(i).zfill(2) + "_"
        yield id


mid = generate_module_id()
cid = generate_case_id()

if __name__ == "__main__":
    print(f"m: {next(mid)}")
    print(f"c: {next(cid)}")
