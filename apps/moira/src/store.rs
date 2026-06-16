use std::fs;
use std::path::{Path, PathBuf};

use chrono::Local;

use crate::model::Ledger;

pub const DIR_NAME: &str = ".ai";
pub const FILE_NAME: &str = "moira.json";

/// 現在時刻を RFC3339 で返す。
pub fn now() -> String {
    Local::now().to_rfc3339()
}

/// `dir` 配下の台帳パス（`dir/.ai/moira.json`）。
pub fn ledger_path_in(dir: &Path) -> PathBuf {
    dir.join(DIR_NAME).join(FILE_NAME)
}

/// `start` から親方向へ `.ai/moira.json` を探索する（git のように上方探索）。
pub fn find_ledger_path(start: &Path) -> Option<PathBuf> {
    let mut dir = Some(start);
    while let Some(current) = dir {
        let candidate = ledger_path_in(current);
        if candidate.is_file() {
            return Some(candidate);
        }
        dir = current.parent();
    }
    None
}

pub fn load(path: &Path) -> Result<Ledger, String> {
    let text =
        fs::read_to_string(path).map_err(|e| format!("{} を読めない: {e}", path.display()))?;
    serde_json::from_str(&text).map_err(|e| format!("{} の解析に失敗: {e}", path.display()))
}

pub fn save(path: &Path, ledger: &Ledger) -> Result<(), String> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)
            .map_err(|e| format!("{} を作成できない: {e}", parent.display()))?;
    }
    let text = serde_json::to_string_pretty(ledger).map_err(|e| format!("JSON 生成に失敗: {e}"))?;
    fs::write(path, text + "\n").map_err(|e| format!("{} に書けない: {e}", path.display()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::model::{Ledger, Status};

    fn tmpdir() -> PathBuf {
        let unique = format!(
            "moira-test-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        );
        let dir = std::env::temp_dir().join(unique);
        fs::create_dir_all(&dir).unwrap();
        dir
    }

    #[test]
    fn save_then_load_roundtrip() {
        let dir = tmpdir();
        let path = ledger_path_in(&dir);
        let mut ledger = Ledger::default();
        ledger.add_task("a", "t0");
        save(&path, &ledger).unwrap();

        let loaded = load(&path).unwrap();
        assert_eq!(loaded.tasks.len(), 1);
        assert_eq!(loaded.tasks[0].title, "a");
        assert_eq!(loaded.next_id, 2);
    }

    #[test]
    fn add_assigns_stable_incrementing_ids() {
        let mut ledger = Ledger::default();
        let a = ledger.add_task("a", "t");
        let b = ledger.add_task("b", "t");
        assert_eq!((a, b), (1, 2));

        // 削除しても id は再利用しない。
        ledger.remove_task(a).unwrap();
        let c = ledger.add_task("c", "t");
        assert_eq!(c, 3);
    }

    #[test]
    fn status_transitions_and_missing() {
        let mut ledger = Ledger::default();
        let id = ledger.add_task("a", "t0");
        ledger.set_status(id, Status::InProgress, "t1").unwrap();
        assert_eq!(ledger.tasks[0].status, Status::InProgress);
        assert_eq!(ledger.tasks[0].updated_at, "t1");
        assert!(ledger.set_status(999, Status::Done, "t").is_err());
    }

    #[test]
    fn remove_missing_errors() {
        let mut ledger = Ledger::default();
        assert!(ledger.remove_task(1).is_err());
    }

    #[test]
    fn meta_and_decisions() {
        let mut ledger = Ledger::default();
        ledger.meta.goal = Some("g".into());
        ledger.add_decision("d1", "t1");
        ledger.add_decision("d2", "t2");
        assert_eq!(ledger.meta.decisions.len(), 2);
        assert_eq!(ledger.meta.decisions[0].text, "d1");
    }

    #[test]
    fn find_walks_upward() {
        let dir = tmpdir();
        let nested = dir.join("a").join("b");
        fs::create_dir_all(&nested).unwrap();
        let path = ledger_path_in(&dir);
        save(&path, &Ledger::default()).unwrap();

        let found = find_ledger_path(&nested).unwrap();
        assert_eq!(found, path);
    }

    #[test]
    fn status_parses() {
        assert_eq!("todo".parse::<Status>().unwrap(), Status::Todo);
        assert_eq!("in_progress".parse::<Status>().unwrap(), Status::InProgress);
        assert!("bogus".parse::<Status>().is_err());
    }
}
