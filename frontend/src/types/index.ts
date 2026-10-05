export type Role='admin'|'manager'|'developer'
export type Priority='low'|'medium'|'high'
export interface User {id:number; email:string; role:Role}
export interface Task {id:number; title:string; description:string; priority:Priority; due_date:string|null; position:number; column_id:number; assignee_id:number|null}
export interface Column {id:number; name:string; position:number; wip_limit:number|null; tasks:Task[]}
export interface Board {id:number; name:string; project_id:number; columns:Column[]}
export interface Project {id:number; name:string; description:string}
