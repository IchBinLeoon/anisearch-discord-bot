use std::collections::{HashMap, HashSet};

struct TrieNode {
    children: HashMap<char, TrieNode>,
    original_words: HashSet<String>,
}

impl TrieNode {
    fn new() -> Self {
        Self {
            children: HashMap::new(),
            original_words: HashSet::new(),
        }
    }
}

pub struct Trie {
    root: TrieNode,
}

impl Trie {
    pub fn new() -> Self {
        Self {
            root: TrieNode::new(),
        }
    }

    pub fn insert(&mut self, word: &str) {
        let mut current = &mut self.root;

        for c in word.to_ascii_lowercase().chars() {
            current = current.children.entry(c).or_insert_with(TrieNode::new);
        }

        current.original_words.insert(word.to_string());
    }

    pub fn search(&self, prefix: &str, limit: usize) -> Vec<String> {
        let mut current = &self.root;

        for c in prefix.to_ascii_lowercase().chars() {
            match current.children.get(&c) {
                Some(node) => current = node,
                None => return vec![],
            }
        }

        let mut res = vec![];
        let mut stack = vec![current];

        while let Some(node) = stack.pop() {
            for original_word in &node.original_words {
                res.push(original_word.clone());

                if res.len() >= limit {
                    return res;
                }
            }

            for child in node.children.values() {
                stack.push(child);
            }
        }

        res
    }
}
