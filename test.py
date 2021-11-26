#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 18:49:00 2021

@author: jmg
"""
import json

def test():
    test_str = 'abcdefghi'
    indexes = [(1,7), (2,4), (3,4), (5,7), (6,7)]
    ordering = [c for c in 'abcdefghi']
    info = {
            (1,7): [c for c in test_str[1:8]],
            (2,4): [c for c in test_str[2:5]],
            (3,4): [c for c in test_str[3:5]],
            (5,7): [c for c in test_str[5:8]],
            (6,7): [c for c in test_str[6:8]]
        }
    def within_range(r_one, r_two):
        return r_two[1] <= r_one[1] and r_two[0] > r_one[0]
    
    seen_ranges = {}            
    indexes = [x for x in info]
    for i in range(len(indexes)-1, -1, -1):
        index_range = indexes[i]
        nodes_in_range = info[index_range]
        contained_ranges = [k for k in seen_ranges if within_range(index_range, k)]
        if len(contained_ranges) == 0 and index_range not in seen_ranges:
            seen_ranges[index_range] = nodes_in_range
        else:
            current_entry = contained_ranges[-1]
            
            current_start_index = index_range[0]
            amount_to_prepend =  current_entry[0] - current_start_index
            new_entry = []
            for j in range(current_start_index, current_start_index + amount_to_prepend):
                new_entry.append(ordering[j])
            contained_ranges.reverse()
            for r in contained_ranges:
                new_entry.append(seen_ranges[r])
                seen_ranges.pop(r, None)
            seen_ranges[index_range] = new_entry
   
    

    final_range = list(seen_ranges.keys())[0]
    final_nested_structure = []
    for i in range(final_range[0]):
        final_nested_structure.append(ordering[i])
    final_nested_structure.append(seen_ranges[final_range])
    total_nested_count = 0
    
    for i in range(final_range[1]+1, len(ordering)):
        final_nested_structure.append(ordering[i])
    
    print(final_nested_structure)
    def recur_print(nested_list, indent_level=0):
        for x in nested_list:
            
            if isinstance(x, list):
                print("INDENTING")
                indent_level += 1
                recur_print(x, indent_level)
                indent_level -= 1
                
            else:
                tab_str = indent_level * '\t'
                print(f'{tab_str}{x}')
    recur_print(final_nested_structure)
    
if __name__ == "__main__":
    test()