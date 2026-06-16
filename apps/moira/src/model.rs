use serde::{Deserialize, Serialize};

/// タスクの状態。zeus の 未着手 / 進行中 / 完了 に対応する。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Status {
    Todo,
    InProgress,
    Done,
}

impl Status {
    /// 一覧表示用のマーカー。
    pub fn marker(&self) -> &'static str {
        match self {
            Status::Todo => "[ ]",
            Status::InProgress => "[~]",
            Status::Done => "[x]",
        }
    }
}

impl std::str::FromStr for Status {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "todo" => Ok(Status::Todo),
            "in_progress" | "in-progress" | "doing" => Ok(Status::InProgress),
            "done" => Ok(Status::Done),
            other => Err(format!("不明なステータス: {other} (todo|in_progress|done)")),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Task {
    pub id: u64,
    pub title: String,
    pub status: Status,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Decision {
    pub at: String,
    pub text: String,
}

/// 再開コンテキスト。要約で失われやすい「なぜ・どこ・次」を保持する。
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct Meta {
    #[serde(default)]
    pub goal: Option<String>,
    #[serde(default)]
    pub current: Option<String>,
    #[serde(default)]
    pub next: Option<String>,
    #[serde(default)]
    pub decisions: Vec<Decision>,
}

/// `.ai/moira.json` の中身全体。
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Ledger {
    pub version: u32,
    pub next_id: u64,
    #[serde(default)]
    pub meta: Meta,
    #[serde(default)]
    pub tasks: Vec<Task>,
}

impl Default for Ledger {
    fn default() -> Self {
        Ledger {
            version: 1,
            next_id: 1,
            meta: Meta::default(),
            tasks: Vec::new(),
        }
    }
}

impl Ledger {
    /// タスクを追加し、採番した id を返す。`next_id` は単調増加で、削除後も再利用しない。
    pub fn add_task(&mut self, title: &str, now: &str) -> u64 {
        let id = self.next_id;
        self.next_id += 1;
        self.tasks.push(Task {
            id,
            title: title.to_string(),
            status: Status::Todo,
            created_at: now.to_string(),
            updated_at: now.to_string(),
        });
        id
    }

    pub fn set_status(&mut self, id: u64, status: Status, now: &str) -> Result<(), String> {
        let task = self
            .tasks
            .iter_mut()
            .find(|t| t.id == id)
            .ok_or_else(|| format!("タスク {id} が見つからない"))?;
        task.status = status;
        task.updated_at = now.to_string();
        Ok(())
    }

    pub fn remove_task(&mut self, id: u64) -> Result<(), String> {
        let before = self.tasks.len();
        self.tasks.retain(|t| t.id != id);
        if self.tasks.len() == before {
            return Err(format!("タスク {id} が見つからない"));
        }
        Ok(())
    }

    pub fn add_decision(&mut self, text: &str, now: &str) {
        self.meta.decisions.push(Decision {
            at: now.to_string(),
            text: text.to_string(),
        });
    }
}
