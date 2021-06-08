from utility_functions import *


def x_shifts_only_test(results, validation_mask, valid_masks):
     for key, result in results.items():
        if validation_mask[key]:
            assert(result in valid_masks)

def add_soft_sequence_max_test(title, results, hard_max, soft_max, obj):
    forbid_max_test(results, hard_max)
    penalize_max_test(title, results, hard_max, soft_max, obj)

def add_soft_sequence_min_test(title, results, hard_min, soft_min, obj, prior):
    forbid_min_test(results, hard_min)
    penalize_min_test(title, results, hard_min, soft_min, obj, prior)


def forbid_max_test(results, hard_max):
    for key, result in results.items():
        assert(not detect_pattern(result, "1" * (hard_max + 1)))

def penalize_max_test(title, results, hard_max, soft_max, obj):
    print(title)
    print(f"Objective function: {obj}")
    for diff in range(soft_max, hard_max + 1):
        partial_sum = 0
        for key, result in results.items():
            partial_sum += detect_pattern_soft(result, "0" + "1" * diff)
            partial_sum += detect_pattern_soft(result[:diff+1], "1" * diff)
        print(f"\t{diff} from range {soft_max} to {hard_max}: {partial_sum}")
        print()

def forbid_min_test(results, hard_min, prior = None, post = None):
    if prior is None and post is not None:
        for key, result in results.items():
            for idx in range(len(result[:-hard_min])):
                if post.shifts[key][idx + hard_min]:
                    for i in range(hard_min + 1):
                        assert(detect_pattern(result[idx + 1: idx + i + 1], "0" * i))

    if prior != None and prior.continue_shifts:
        for key, result in results.items():
            for idx in range(len(result[:-hard_min])):
                if prior.shifts[key][idx] and not prior.shifts[key][idx + 1]:
                    for i in range(hard_min + 1):
                        assert(detect_pattern(result[idx + 1: idx + i + 1], "0" * i))

def penalize_min_test(title, results, hard_min, soft_min, obj, prior = None):
    print(title)
    print(f"Objective function: {obj}")
    for diff in range(hard_min, soft_min+1):
        if prior != None and prior.continue_shifts:
            partial_sum = 0
            for key, result in results.items():
                for idx in range(len(result[:-hard_min])):
                    if prior.shifts[key][idx] and not prior.shifts[key][idx + 1]:
                        if detect_pattern(result[idx + 1: idx + diff + 2], "0" * diff + "1"):
                            partial_sum += 1
            print(f"\t{diff} from range {hard_min} to {soft_min}: {partial_sum}")
            print()
                    