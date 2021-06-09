from utility_functions import *
from scheduling_funtions import *


def x_shifts_only_test(results, validation_mask, valid_masks):
    for key, result in results.items():
        if validation_mask[key]:
            assert(result in valid_masks)


def add_soft_sequence_max_test(title, results, hard_max, soft_max, obj, prior=None, post=None):
    forbid_max_test(results, hard_max, prior, post)
    penalize_max_test(title, results, hard_max, soft_max, obj, prior, post)


def add_soft_sequence_min_test(title, results, hard_min, soft_min, obj, prior=None, post=None):
    forbid_min_test(results, hard_min, prior, post)
    penalize_min_test(title, results, hard_min, soft_min, obj, prior, post)

def soft_sum_test(title, results, hard_min, soft_min, hard_max, soft_max, obj):
    print(title)
    print(f"Objective function: {obj}")
    for staff, result in results.items():
        print()

def distribution_test(title, results, target_shifts, obj):
    print(title)
    print(f"Objective function: {obj}")

    partial_sum = 0
    for staff, result in results.items():
        staff_sum = sum(result)
        partial_sum += abs(target_shifts - staff_sum)
    print(f"Difference from target of {target_shifts}: {partial_sum}")

def forbid_max_test(results, hard_max, prior=None, post=None):
    prior_exists = prior is not None
    post_exists = post is not None
    pred_check = False
    continue_pattern = prior_exists and prior.continue_shifts
    grow_pred = (prior_exists and prior.continue_shifts)

    for staff, result in results.items():
        for length in window_length(hard_max, grow_pred):
            for start in shift_window(result, length, prior, post):
                if post_exists and prior_exists:
                    if prior.shifts[staff][start:start+len(prior.choices)] == prior.choices:
                        if post.shifts[staff][start + len(prior.choices) + length:start + len(prior.choices)+length+len(post.choices)] == post.choices:
                            pred_check = True
                if prior_exists and not post_exists:
                    if prior.shifts[staff][start:start+len(prior.choices)] == prior.choices:
                        pred_check = True
                if post_exists and not prior_exists:
                    if post.shifts[staff][start+length:start+length+len(post.choices)] == post.choices:
                        pred_check = True
                if pred_check:
                    if continue_pattern:
                        if start > window_size(result, length, prior, post) - len(prior.choices) - 1 or prior.shifts[staff][start + len(prior.choices)]:
                            pred_check = False
                            continue
                        assert(detect_pattern(
                            result[start + len(prior.choices): start + len(prior.choices) + length + 1], "1" * length))
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
    grow_pred = continue_pattern or (
        not prior_exists and not post_exists)

    for staff, result in results.items():
        for length in window_length(hard_min, grow_pred):
            for start in shift_window(result, length, prior, post):
                if post_exists and prior_exists:
                    if prior.shifts[staff][start:start+len(prior.choices)] == prior.choices:
                        if post.shifts[staff][start + len(prior.choices) + length:start + len(prior.choices)+length+len(post.choices)] == post.choices:
                            pred_check = True
                if prior_exists and not post_exists:
                    if prior.shifts[staff][start:start+len(prior.choices)] == prior.choices:
                        pred_check = True
                if post_exists and not prior_exists:
                    if post.shifts[staff][start+length:start+length+len(post.choices)] == post.choices:
                        pred_check = True
                if pred_check:
                    if continue_pattern:
                        if start > window_size(result, length, prior, post) - len(prior.choices) - 1 or prior.shifts[staff][start + len(prior.choices)]:
                            pred_check = False
                            continue
                        assert(detect_pattern(
                            result[start + len(prior.choices): start + len(prior.choices) + length + 1], "1" * length))
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

    for length in range(hard_min, soft_min + 1):
        partial_sum = 0
        for staff, result in results.items():
            for start in shift_window(result, length, prior, post):
                if post_exists and prior_exists:
                    if prior.shifts[staff][start:start+len(prior.choices)] == prior.choices:
                        if post.shifts[staff][start + len(prior.choices) + length:start + len(prior.choices)+length+len(post.choices)] == post.choices:
                            pred_check = True
                if prior_exists and not post_exists:
                    if prior.shifts[staff][start:start+len(prior.choices)] == prior.choices:
                        pred_check = True
                if post_exists and not prior_exists:
                    if post.shifts[staff][start+length:start+length+len(post.choices)] == post.choices:
                        pred_check = True
                if pred_check:
                    if continue_pattern:
                        if start > window_size(result, length, prior, post) - len(prior.choices) - 1 or prior.shifts[staff][start + len(prior.choices)]:
                            pred_check = False
                            continue
                        partial_sum += detect_pattern_soft(
                            result[start + len(prior.choices): start + len(prior.choices) + length + 1], "1" * length + "0")
                        pred_check = False
                    elif prior_exists:
                        detect_pattern_soft(
                            result[start + len(prior.choices): start + len(prior.choices) + length + 1], "1" * length + "0")
                    else:
                        detect_pattern_soft(
                            result[start: start + length + 1], "1" * length + "0")
                        pred_check = False
            if not prior_exists and not post_exists:
                partial_sum += detect_pattern_soft(result, "0" + "1" * length)
                partial_sum += detect_pattern_soft(
                    result[:length+1], "1" * length)
        print(f"\t{length} from range {hard_min} to {soft_min}: {partial_sum}")
        print()
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
                if post_exists and prior_exists:
                    if prior.shifts[staff][start:start+len(prior.choices)] == prior.choices:
                        if post.shifts[staff][start + len(prior.choices) + length:start + len(prior.choices)+length+len(post.choices)] == post.choices:
                            pred_check = True
                if prior_exists and not post_exists:
                    if prior.shifts[staff][start:start+len(prior.choices)] == prior.choices:
                        pred_check = True
                if post_exists and not prior_exists:
                    if post.shifts[staff][start+length:start+length+len(post.choices)] == post.choices:
                        pred_check = True
                if pred_check:
                    if continue_pattern:
                        if start > window_size(result, length, prior, post) - len(prior.choices) - 1 or prior.shifts[staff][start + len(prior.choices)]:
                            pred_check = False
                            continue
                        partial_sum += detect_pattern_soft(
                            result[start + len(prior.choices): start + len(prior.choices) + length + 1], "1" * length + "0")
                        pred_check = False
                    elif prior_exists:
                        detect_pattern_soft(
                            result[start + len(prior.choices): start + len(prior.choices) + length + 1], "1" * length + "0")
                    else:
                        detect_pattern_soft(
                            result[start: start + length + 1], "1" * length + "0")
                        pred_check = False
            if not prior_exists and not post_exists:
                partial_sum += detect_pattern_soft(result, "0" + "1" * length)
                partial_sum += detect_pattern_soft(
                    result[:length], "1" * length)
        print(f"\t{length} from range {soft_max} to {hard_max}: {partial_sum}")
        print()
    print()