#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>
#include "trie_engine.h"

// Global root node
static TrieNode* root = NULL;

// Create a new trie node
static TrieNode* create_node(void) {
    TrieNode *node = (TrieNode *)calloc(1, sizeof(TrieNode));
    if (!node) {
        fprintf(stderr, "Error: Failed to allocate memory for trie node\n");
        return NULL;
    }
    return node;
}

// Initialize the trie
void init_trie(void) {
    if (root == NULL) {
        root = create_node();
        if (!root) {
            fprintf(stderr, "Error: Failed to initialize trie\n");
            exit(1);
        }
    }
}

// Convert string to lowercase and remove non-alphabetic characters
static void normalize_string(char *str) {
    if (!str) return;
    
    char *write = str;
    for (char *read = str; *read; read++) {
        if (isalpha(*read)) {
            *write++ = tolower(*read);
        }
    }
    *write = '\0';
}

// Insert a rule into the trie
void insert_rule(const char *rule) {
    if (!rule) return;
    
    if (!root) init_trie();
    
    // Handle empty string specially
    if (rule[0] == '\0') {
        root->is_end_of_rule = 1;
        return;
    }
    
    // Create a copy of the rule for normalization
    char *normalized = strdup(rule);
    if (!normalized) {
        fprintf(stderr, "Error: Failed to allocate memory for rule normalization\n");
        return;
    }
    
    normalize_string(normalized);
    
    // Skip if no alphabetic characters
    if (normalized[0] == '\0') {
        free(normalized);
        return;
    }
    
    TrieNode *current = root;
    for (int i = 0; normalized[i] != '\0'; i++) {
        int index = normalized[i] - 'a';
        if (current->children[index] == NULL) {
            current->children[index] = create_node();
            if (!current->children[index]) {
                free(normalized);
                return;
            }
        }
        current = current->children[index];
    }
    current->is_end_of_rule = 1;
    free(normalized);
}

// Search for a rule in the trie
int search_rule(const char *rule) {
    if (!rule || !root) return 0;
    
    // Handle empty string specially
    if (rule[0] == '\0') {
        return root->is_end_of_rule;
    }
    
    // Create a copy of the rule for normalization
    char *normalized = strdup(rule);
    if (!normalized) {
        fprintf(stderr, "Error: Failed to allocate memory for rule normalization\n");
        return 0;
    }
    
    normalize_string(normalized);
    
    // Skip if no alphabetic characters
    if (normalized[0] == '\0') {
        free(normalized);
        return 0;
    }
    
    TrieNode *current = root;
    for (int i = 0; normalized[i] != '\0'; i++) {
        int index = normalized[i] - 'a';
        if (current->children[index] == NULL) {
            free(normalized);
            return 0;
        }
        current = current->children[index];
    }
    
    int result = current->is_end_of_rule;
    free(normalized);
    return result;
}

// Helper function to free a trie node
static void free_trie_node(TrieNode *node) {
    if (!node) return;
    for (int i = 0; i < 26; i++) {
        if (node->children[i] != NULL) {
            free_trie_node(node->children[i]);
        }
    }
    free(node);
}

// Free the trie
void free_trie(void) {
    if (root) {
        free_trie_node(root);
        root = NULL;
    }
}

// Example usage:
// TrieNode *root = create_node();
// insert(root, "example");
// printf("%d\n", search(root, "example"));  // Output: 1
// free_trie(root);

