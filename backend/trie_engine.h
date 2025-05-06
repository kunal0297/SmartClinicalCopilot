#ifndef TRIE_ENGINE_H
#define TRIE_ENGINE_H

// Define the structure for a trie node
typedef struct TrieNode {
    struct TrieNode *children[26]; // Assuming only lowercase a-z
    int is_end_of_rule; // Flag to mark the end of a rule
} TrieNode;

// Function declarations
void init_trie(void);
void insert_rule(const char *rule);
int search_rule(const char *rule);
void free_trie(void);

#endif // TRIE_ENGINE_H 