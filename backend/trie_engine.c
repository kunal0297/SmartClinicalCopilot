#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Define the structure for a trie node
typedef struct TrieNode {
    struct TrieNode *children[26]; // Assuming only lowercase a-z
    int is_end_of_rule; // Flag to mark the end of a rule
} TrieNode;

// Create a new trie node
TrieNode* create_node() {
    TrieNode *node = (TrieNode *)malloc(sizeof(TrieNode));
    if (!node) return NULL;
    node->is_end_of_rule = 0;
    for (int i = 0; i < 26; i++) {
        node->children[i] = NULL;
    }
    return node;
}

// Insert a rule into the trie
void insert(TrieNode *root, const char *rule) {
    TrieNode *current = root;
    for (int i = 0; rule[i] != '\0'; i++) {
        char c = rule[i];
        if (c < 'a' || c > 'z') continue; // Skip non-lowercase chars for safety
        int index = c - 'a'; 
        if (current->children[index] == NULL) {
            current->children[index] = create_node();
        }
        current = current->children[index];
    }
    current->is_end_of_rule = 1; // Mark the end of the rule
}

// Search for a rule in the trie
int search(TrieNode *root, const char *rule) {
    TrieNode *current = root;
    for (int i = 0; rule[i] != '\0'; i++) {
        char c = rule[i];
        if (c < 'a' || c > 'z') return 0; // Reject invalid char
        int index = c - 'a';
        if (current->children[index] == NULL) {
            return 0; // Rule not found
        }
        current = current->children[index];
    }
    return current->is_end_of_rule; // Return 1 if it's a valid rule
}

// Free the trie
void free_trie(TrieNode *root) {
    if (!root) return;
    for (int i = 0; i < 26; i++) {
        if (root->children[i] != NULL) {
            free_trie(root->children[i]);
        }
    }
    free(root);
}
