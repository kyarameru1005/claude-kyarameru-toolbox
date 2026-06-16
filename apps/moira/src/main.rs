use std::env;
use std::process;

use clap::{Parser, Subcommand};

use moira::model::{Ledger, Status};
use moira::store;

#[derive(Parser)]
#[command(
    name = "moira",
    version,
    about = "タスクと再開コンテキストを .ai/moira.json で管理する"
)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// .ai/moira.json を作成する
    Init {
        #[arg(long)]
        force: bool,
    },
    /// タスクを追加する
    Add { title: String },
    /// タスク一覧を表示する
    List {
        #[arg(long)]
        json: bool,
    },
    /// タスクを進行中にする
    Start { id: u64 },
    /// タスクを完了にする
    Done { id: u64 },
    /// タスクのステータスを変更する (todo|in_progress|done)
    Status { id: u64, state: String },
    /// タスクを削除する
    Remove { id: u64 },
    /// 再開ビュー（meta + タスク）を表示する
    Show {
        #[arg(long)]
        json: bool,
    },
    /// 目的を設定する
    Goal { text: String },
    /// 現在地を設定する
    At { text: String },
    /// 次の一手を設定する
    Next { text: String },
    /// 決定ログに追記する
    Decide { text: String },
}

fn main() {
    if let Err(e) = run(Cli::parse()) {
        eprintln!("error: {e}");
        process::exit(1);
    }
}

fn run(cli: Cli) -> Result<(), String> {
    let cwd = env::current_dir().map_err(|e| format!("cwd 取得失敗: {e}"))?;

    // init は台帳探索なしで cwd 直下に作成する。
    if let Command::Init { force } = &cli.command {
        let path = store::ledger_path_in(&cwd);
        if path.exists() && !force {
            return Err(format!("{} は既に存在する (--force で上書き)", path.display()));
        }
        store::save(&path, &Ledger::default())?;
        println!("初期化しました: {}", path.display());
        return Ok(());
    }

    let path = store::find_ledger_path(&cwd)
        .ok_or_else(|| ".ai/moira.json が見つからない。先に `moira init` を実行してください".to_string())?;
    let mut ledger = store::load(&path)?;
    let now = store::now();

    match cli.command {
        Command::Init { .. } => unreachable!("init は上で処理済み"),
        Command::Add { title } => {
            let id = ledger.add_task(&title, &now);
            store::save(&path, &ledger)?;
            println!("追加: ({id}) {title}");
        }
        Command::List { json } => {
            if json {
                print_json(&ledger.tasks)?;
            } else {
                print_tasks(&ledger);
            }
        }
        Command::Start { id } => {
            ledger.set_status(id, Status::InProgress, &now)?;
            store::save(&path, &ledger)?;
            println!("進行中: ({id})");
        }
        Command::Done { id } => {
            ledger.set_status(id, Status::Done, &now)?;
            store::save(&path, &ledger)?;
            println!("完了: ({id})");
        }
        Command::Status { id, state } => {
            let status: Status = state.parse()?;
            ledger.set_status(id, status, &now)?;
            store::save(&path, &ledger)?;
            println!("更新: ({id}) -> {state}");
        }
        Command::Remove { id } => {
            ledger.remove_task(id)?;
            store::save(&path, &ledger)?;
            println!("削除: ({id})");
        }
        Command::Show { json } => {
            if json {
                print_json(&ledger)?;
            } else {
                print_show(&ledger);
            }
        }
        Command::Goal { text } => {
            ledger.meta.goal = Some(text.clone());
            store::save(&path, &ledger)?;
            println!("目的を設定: {text}");
        }
        Command::At { text } => {
            ledger.meta.current = Some(text.clone());
            store::save(&path, &ledger)?;
            println!("現在地を設定: {text}");
        }
        Command::Next { text } => {
            ledger.meta.next = Some(text.clone());
            store::save(&path, &ledger)?;
            println!("次の一手を設定: {text}");
        }
        Command::Decide { text } => {
            ledger.add_decision(&text, &now);
            store::save(&path, &ledger)?;
            println!("決定を記録: {text}");
        }
    }
    Ok(())
}

fn print_tasks(ledger: &Ledger) {
    if ledger.tasks.is_empty() {
        println!("(タスクなし)");
        return;
    }
    for task in &ledger.tasks {
        println!("{} ({}) {}", task.status.marker(), task.id, task.title);
    }
}

fn print_show(ledger: &Ledger) {
    let meta = &ledger.meta;
    println!("# 再開ビュー");
    println!("目的    : {}", meta.goal.as_deref().unwrap_or("(未設定)"));
    println!("現在地  : {}", meta.current.as_deref().unwrap_or("(未設定)"));
    println!("次の一手: {}", meta.next.as_deref().unwrap_or("(未設定)"));
    println!();
    println!("## 決定ログ");
    if meta.decisions.is_empty() {
        println!("(なし)");
    } else {
        for decision in &meta.decisions {
            println!("- {} {}", decision.at, decision.text);
        }
    }
    println!();
    println!("## タスク");
    print_tasks(ledger);
}

fn print_json<T: serde::Serialize>(value: &T) -> Result<(), String> {
    let text = serde_json::to_string_pretty(value).map_err(|e| format!("JSON 生成失敗: {e}"))?;
    println!("{text}");
    Ok(())
}
