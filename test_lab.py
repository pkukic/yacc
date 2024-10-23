import os
import subprocess
import shutil

def main():
    # Define ROOT_DIR and ANALIZATOR_DIR
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    ANALIZATOR_DIR = os.path.join(ROOT_DIR, 'analizator')

    # Loop over the range 1 to 13 (inclusive)
    for i in range(1, 14):
        # Remove files if they exist
        reductions_path = os.path.join(ANALIZATOR_DIR, 'reductions.txt')
        lr_table_path = os.path.join(ANALIZATOR_DIR, 'LR_table.txt')

        if os.path.exists(reductions_path):
            os.remove(reductions_path)
        if os.path.exists(lr_table_path):
            os.remove(lr_table_path)

        print("#################################################################################################")
        print(f"Test {i}")

        # Commented out condition (like in the bash script)
        # if i == 8 or i == 13:
        #     continue

        # Run the GSA.py script
        test_san_path = os.path.join(ROOT_DIR, f"testovi/test_{i}/test.san")
        subprocess.run(['python3', 'GSA.py'], stdin=open(test_san_path), check=True)

        # Run the SA.py script and capture the output
        test_in_path = os.path.join(ROOT_DIR, f"testovi/test_{i}/test.in")
        test_out_path = os.path.join(ROOT_DIR, f"testovi/test_{i}/test.out")
        with open(test_in_path) as test_in:
            result = subprocess.run(['python3', os.path.join(ANALIZATOR_DIR, 'SA.py')],
                                    stdin=test_in, capture_output=True, text=True)
        
        # Compare output to the expected result using `diff`
        with open(test_out_path) as test_out:
            expected_output = test_out.read()
        
        if result.stdout != expected_output:
            print("FAIL")
            print(result.stdout)
        else:
            print("OK")

        # Clean up by removing the files again
        if os.path.exists(reductions_path):
            os.remove(reductions_path)
        if os.path.exists(lr_table_path):
            os.remove(lr_table_path)

if __name__ == "__main__":
    main()

