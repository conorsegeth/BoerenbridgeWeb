import random

if __name__ == '__main__':
    nums = []
    for i in range(15):
        bruh = round(random.gauss(0, 1.2), 2)
        nums.append(bruh)

print(nums)