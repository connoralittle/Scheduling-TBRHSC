from utility_functions import *
from scheduling_funtions import *


def x_shifts_only_test(results, validation_mask, valid_masks):
    for key, result in results.items():
        if validation_mask[key]:
            assert(result in valid_masks)


def add_soft_sequence_max_test(title, results, hard_max, soft_max, obj, prior=None, post=None):
    forbid_max_test(results, hard_max, prior, post)
    penalize_max_test(title, results, hard_max, soft_max, obj)


def add_soft_sequence_min_test(title, results, hard_min, soft_min, obj, prior=None, post=None):
    forbid_min_test(results, hard_min, prior, post)
    penalize_min_test(title, results, hard_min, soft_min, obj, prior)


# def forbid_max_test(results, hard_max):
#     for key, result in results.items():
#         assert(not detect_pattern(result, "1" * (hard_max + 1)))

def forbid_max_test(results, hard_max, prior=None, post=None):
    prior_exists = prior is not None
    post_exists = post is not None
    pred_check = False
    continue_pattern = prior_exists and prior.continue_shifts
    grow_pred = (prior_exists and prior.continue_shifts)

    for staff, result in results.items():
        for length in window_length(hard_max, grow_pred):
            for start in shift_window(result, length, prior, post):
                if prior_exists and prior.shifts[staff][start:start+len(prior.choices)] == prior.choices:
                    pred_check = True
                if post_exists:
                    if prior_exists and post.shifts[staff][start:start+len(prior.choices)+length+len(post.choices)+1] == post.choices:
                        pred_check = True
                    elif post.shifts[staff][start:start+length+len(post.choices)] == post.choices:
                        pred_check = True
                if pred_check:
                    if continue_pattern and not (start == window_size(result, length, prior, post) - 1):
                        assert(detect_pattern(result[start: start + length + 1], "1" * length) or [
                               prior.shifts[staff][start+len(prior.choices)+1]])
                    elif prior_exists:
                        assert(detect_pattern(
                            result[start + len(prior.choices): start + len(prior.choices) + length + 1], "1" * length))
                    else:
                        assert(detect_pattern(
                            result[start: start + length + 1], "1" * length))
                    pred_check = False
            if not prior_exists and not post_exists:
                assert(not detect_pattern(result, "1" * (length + 1)))


def forbid_min_test(results, hard_min, prior=None, post=None):
    prior_exists = prior is not None
    post_exists = post is not None
    pred_check = False
    continue_pattern = prior_exists and prior.continue_shifts
    grow_pred = (prior_exists and prior.continue_shifts) or (
        not prior_exists and not post_exists)

    for staff, result in results.items():
        for length in window_length(hard_min, grow_pred):
            for start in shift_window(result, length, prior, post):
                if prior_exists and prior.shifts[staff][start:start+len(prior.choices)] == prior.choices:
                    pred_check = True
                if post_exists:
                    if prior_exists and post.shifts[staff][start:start+len(prior.choices)+length+len(post.choices)+1] == post.choices:
                        pred_check = True
                    elif post.shifts[staff][start:start+length+len(post.choices)] == post.choices:
                        pred_check = True
                if pred_check:
                    if continue_pattern and not (start == window_size(result, length, prior, post) - 1):
                        assert(detect_pattern(result[start: start + length + 1], "1" * length) or [
                               prior.shifts[staff][start+len(prior.choices)+1]])
                    elif prior_exists:
                        assert(detect_pattern(
                            result[start + len(prior.choices): start + len(prior.choices) + length + 1], "1" * length))
                    else:
                        assert(detect_pattern(
                            result[start: start + length + 1], "1" * length))
                    pred_check = False
            if not prior_exists and not post_exists:
                assert(detect_pattern(result, "1" * length))


def penalize_min_test(title, results, hard_min, soft_min, obj, prior=None, post=None):
    print(title)
    print(f"Objective function: {obj}")
    prior_exists = prior is not None
    post_exists = post is not None
    pred_check = False
    continue_pattern = prior_exists and prior.continue_shifts

    for length in range(hard_min, soft_min+1):
        partial_sum = 0
        for staff, result in results.items():
            for start in shift_window(result, length, prior, post):
                if prior_exists and prior.shifts[staff][start:start+len(prior.choices)] == prior.choices:
                    pred_check = True
                if post_exists:
                    if prior_exists and post.shifts[staff][start:start+len(prior.choices)+length+len(post.choices)+1] == post.choices:
                        pred_check = True
                    elif post.shifts[staff][start:start+length+len(post.choices)] == post.choices:
                        pred_check = True
                if pred_check:
                    if continue_pattern and not (start == window_size(result, length, prior, post) - 1):
                        if not prior.shifts[staff][start+len(prior.choices)+1]:
                            partial_sum += detect_pattern_soft(
                                result[start: start + length + 1], "1" * length + "0")
                            if start + len(prior.choices)+length+1 == len(result) + 1:
                                partial_sum += detect_pattern_soft(
                                    result[start: start + length + 1], "1" * length)
                            pred_check = False
                    elif prior_exists:
                        partial_sum += detect_pattern_soft(result[start+len(
                            prior.choices):start + len(prior.choices)+length+1], "1" * length + "0")
                        if start + len(prior.choices)+length+1 == len(result) + 1:
                            partial_sum += detect_pattern_soft(result[start+len(
                                prior.choices):start + len(prior.choices)+length+1], "1" * length)
                        pred_check = False
            if not prior_exists and not post_exists:
                partial_sum += detect_pattern_soft(result, "0" + "1" * length)
                partial_sum += detect_pattern_soft(
                    result[:length+1], "1" * length)
        print(f"\t{length} from range {hard_min} to {soft_min}: {partial_sum}")
        print()


def penalize_max_test(title, results, hard_max, soft_max, obj, prior=None, post=None):
    print(title)
    print(f"Objective function: {obj}")
    prior_exists = prior is not None
    post_exists = post is not None
    pred_check = False
    continue_pattern = prior_exists and prior.continue_shifts

    for length in range(soft_max, hard_max + 1):
        partial_sum = 0
        for staff, result in results.items():
            for start in shift_window(result, length, prior, post):
                if prior_exists and prior.shifts[staff][start:start+len(prior.choices)] == prior.choices:
                    pred_check = True
                if post_exists:
                    if prior_exists and post.shifts[staff][start:start+len(prior.choices)+length+len(post.choices)+1] == post.choices:
                        pred_check = True
                    elif post.shifts[staff][start:start+length+len(post.choices)] == post.choices:
                        pred_check = True
                if pred_check:
                    print("here")
                    if continue_pattern and not (start == window_size(result, length, prior, post) - 1):
                        if not prior.shifts[staff][start+len(prior.choices)+1]:
                            partial_sum += detect_pattern_soft(
                                result[start: start + length + 1], "1" * length + "0")
                            if start + len(prior.choices)+length+1 == len(result) + 1:
                                partial_sum += detect_pattern_soft(
                                    result[start: start + length + 1], "1" * length)
                            pred_check = False
                    elif prior_exists:
                        partial_sum += detect_pattern_soft(result[start+len(
                            prior.choices):start + len(prior.choices)+length+1], "1" * length + "0")
                        if start + len(prior.choices)+length+1 == len(result) + 1:
                            partial_sum += detect_pattern_soft(result[start+len(
                                prior.choices):start + len(prior.choices)+length+1], "1" * length)
                        pred_check = False
            if not prior_exists and not post_exists:
                partial_sum += detect_pattern_soft(result, "0" + "1" * length)
                partial_sum += detect_pattern_soft(
                    result[:length], "1" * length)
        print(f"\t{length} from range {soft_max} to {hard_max}: {partial_sum}")
        print()

# def penalize_max_test(title, results, hard_max, soft_max, obj):
#     print(title)
#     print(f"Objective function: {obj}")
#     for diff in range(soft_max, hard_max + 1):
#         partial_sum = 0
#         for key, result in results.items():
#             partial_sum += detect_pattern_soft(result, "0" + "1" * diff)
#             partial_sum += detect_pattern_soft(result[:diff+1], "1" * diff)
#         print(f"\t{diff} from range {soft_max} to {hard_max}: {partial_sum}")
#         print()

# def forbid_min_test(results, hard_min, prior = None, post = None):
#     if prior is None and post is not None:
#         for key, result in results.items():
#             for idx in range(len(result[:-hard_min])):
#                 if post.shifts[key][idx + hard_min]:
#                     for i in range(hard_min + 1):
#                         assert(detect_pattern(result[idx + 1: idx + i + 1], "0" * i))

#     if prior != None and prior.continue_shifts:
#         for key, result in results.items():
#             for idx in range(len(result[:-hard_min])):
#                 if prior.shifts[key][idx] and not prior.shifts[key][idx + 1]:
#                     for i in range(hard_min + 1):
#                         assert(detect_pattern(result[idx + 1: idx + i + 1], "0" * i))

# def penalize_min_test(title, results, hard_min, soft_min, obj, prior = None):
#     print(title)
#     print(f"Objective function: {obj}")
#     for diff in range(hard_min, soft_min+1):
#         if prior != None and prior.continue_shifts:
#             partial_sum = 0
#             for key, result in results.items():
#                 for idx in range(len(result[:-hard_min])):
#                     if prior.shifts[key][idx] and not prior.shifts[key][idx + 1]:
#                         if detect_pattern(result[idx + 1: idx + diff + 2], "0" * diff + "1"):
#                             partial_sum += 1
#             print(f"\t{diff} from range {hard_min} to {soft_min}: {partial_sum}")
#             print()
