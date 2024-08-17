//------------------------------------------------------------------------------
// mutate strategy: move a stmt (not decl)
// usage: moveStmt-mul <path to main.c> --  <position>
//------------------------------------------------------------------------------
#include <sstream>
#include <string>
#include <iostream>
#include <fstream>
#include <stdio.h>
#include <dirent.h>
#include <memory>
#include <map>
#include <set>
#include <vector>
#include <deque>
#include "clang/AST/AST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/AST/ASTContext.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/ASTConsumers.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "llvm/Support/raw_ostream.h"
#include "clang/Lex/Lexer.h"
using namespace std;
using namespace clang;
using namespace clang::driver;
using namespace clang::tooling;

static llvm::cl::OptionCategory VisitAST_Category("usage: moveStmt-mul <path to main.c> --  <position>");
static int64_t position = -1;

// stage 0: get the stmt we need to move (in position)
// stage 1: find all position that can insert this stmt
// stage 2: random choose a position and insert the stmt
static int stage = 0;

static string move_stmt = "";
static vector<int> can_insert_pos;
static bool find_position = 0;
static set<int> can_not_insert;
static int insert_pos = -1;

// By implementing RecursiveASTVisitor, we can specify which AST nodes
// we're interested in by overriding relevant methods.
class MyASTVisitor : public RecursiveASTVisitor<MyASTVisitor> {
public:
  ASTContext *Context=NULL;
  MyASTVisitor(Rewriter &R) : TheRewriter(R) {}

  LangOptions lopt;
  string stmt2str(Stmt *s) {
    SourceLocation b(s->getSourceRange().getBegin()), _e(s->getSourceRange().getEnd());
    SourceLocation e(Lexer::getLocForEndOfToken(_e, 0, TheRewriter.getSourceMgr(), lopt));
    return string(TheRewriter.getSourceMgr().getCharacterData(b),
        TheRewriter.getSourceMgr().getCharacterData(e)-TheRewriter.getSourceMgr().getCharacterData(b));
  }

  bool VisitStmt(Stmt *S) {
    int S_id=S->getID(*Context);
    if(stage==0){
      if (S_id==position){
        cout<<"get stmt: "<<endl;
        move_stmt = stmt2str(S);
        cout<<move_stmt<<endl;
        TheRewriter.ReplaceText(S->getSourceRange(), ";");
      }
      if(find_position){
        can_not_insert.insert(S_id);
        cout<<"can_not_insert: "<<S_id<<endl;
      }
    }else if(stage==1){
      Stmt* parent_Stmt=get_parent();
      if(parent_Stmt!=NULL){
        if(isa<CompoundStmt>(parent_Stmt) && !isa<DeclStmt>(S)){
          if(can_not_insert.find(S_id)==can_not_insert.end()){
            can_insert_pos.push_back(S_id);
          }
        }
      }

      if (isa<IfStmt>(S)){
        IfStmt* IfS= cast<IfStmt>(S);
        Stmt* thenS=IfS->getThen();
        Stmt* elseS=IfS->getElse();
        if(!isa<CompoundStmt>(thenS)){
          if(can_not_insert.find(thenS->getID(*Context))==can_not_insert.end()){
            can_insert_pos.push_back(thenS->getID(*Context));
          }
        }
        if(elseS && !isa<CompoundStmt>(elseS)){
          if(can_not_insert.find(elseS->getID(*Context))==can_not_insert.end()){
            can_insert_pos.push_back(elseS->getID(*Context));
          }
        }
      }
      else if (isa<WhileStmt>(S)){
        WhileStmt* WhileS=cast<WhileStmt>(S);
        Stmt* bodyS=WhileS->getBody();
        if(!isa<CompoundStmt>(bodyS)){
          if(can_not_insert.find(bodyS->getID(*Context))==can_not_insert.end()){
            can_insert_pos.push_back(bodyS->getID(*Context));
          }
        }
      }
      else if (isa<ForStmt>(S)){
        ForStmt* ForS=cast<ForStmt>(S);
        Stmt* bodyS=ForS->getBody();
        if(!isa<CompoundStmt>(bodyS)){
          if(can_not_insert.find(bodyS->getID(*Context))==can_not_insert.end()){
            can_insert_pos.push_back(bodyS->getID(*Context));
          }
        }
      }
    }else if (stage==2){
      if (S_id==insert_pos){
        cout<<"mutate here: insert stmt"<<endl;
        cout<<"will insert: "<<move_stmt<<endl;
        TheRewriter.InsertText(S->getSourceRange().getBegin(), move_stmt+";\n");
        return false;
      }
    }

    return true;
  }

  bool TraverseStmt(Stmt *S) {
    bool result = 0;
    if(Context==NULL){
      llvm::errs() <<"Error: Context is NULL" << "\n";
      return 0;
    }

    int S_id=S->getID(*Context);

    if (S_id==position){
      find_position=1;
    }

    ancestor_nodes.push(S);
    result = RecursiveASTVisitor::TraverseStmt(S);
    ancestor_nodes.pop();

    if (S_id==position){
      find_position=0;
    }
    
    return result;
  }

  Stmt* get_parent(){
    Stmt* self=ancestor_nodes.top();
    ancestor_nodes.pop();
    if(ancestor_nodes.empty()){
      ancestor_nodes.push(self);
      return NULL;
    }
    Stmt* parent=ancestor_nodes.top();
    ancestor_nodes.push(self);
    return parent;
  }

private:
  Rewriter &TheRewriter;
  std::stack<Stmt*> ancestor_nodes;
};

// Implementation of the ASTConsumer interface for reading an AST produced
// by the Clang parser.
class MyASTConsumer : public ASTConsumer {
public:
  MyASTConsumer(Rewriter &R) : Visitor(R),TheRewriter(R) {}

  int CopyFile(char *SourceFile,char *NewFile) 
  {  
    ifstream in; 
    ofstream out;  
    in.open(SourceFile,ios::binary);//
    if(in.fail())//
    {     
        cout<<"Error 1: Fail to open the source file."<<endl;    
        in.close();    
        out.close();    
        return 0; 
    }  
    out.open(NewFile,ios::binary);//
    if(out.fail())//
    {     
        cout<<"Error 2: Fail to create the new file."<<endl;    
        out.close();    
        in.close();    
        return 0; 
    }  
    else//
    {     
        out<<in.rdbuf();    
        out.close();    
        in.close();    
        return 1; 
    } 
  }

  void HandleTranslationUnit(ASTContext &Context) override  {
    /* we can use ASTContext to get the TranslationUnitDecl, which is
       a single Decl that collectively represents the entire source file */
    Visitor.Context=&Context;

    stage = 0;
    CopyFile("main.c", "mainori.c");
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());

    stage = 1;
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());
    int choose_ind=(rand() % (can_insert_pos.size()));
    insert_pos=can_insert_pos[choose_ind];
    cout<<"choose pos: "<<insert_pos<<endl;

    stage = 2;
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());
    TheRewriter.overwriteChangedFiles();
    rename("main.c", "mainvar.c");
    rename("mainori.c", "main.c");
  }

private:
  MyASTVisitor Visitor;
  Rewriter &TheRewriter;
};

// For each source file provided to the tool, a new FrontendAction is created.
class MyFrontendAction : public ASTFrontendAction {
public:
  MyFrontendAction() {}

  int CopyFile(char *SourceFile,char *NewFile) 
  {  
    ifstream in; 
    ofstream out;  
    in.open(SourceFile,ios::binary);//
    if(in.fail())//
    {     
        cout<<"Error 1: Fail to open the source file."<<endl;    
        in.close();    
        out.close();    
        return 0; 
    }  
    out.open(NewFile,ios::binary);//
    if(out.fail())//
    {     
        cout<<"Error 2: Fail to create the new file."<<endl;    
        out.close();    
        in.close();    
        return 0; 
    }  
    else//
    {     
        out<<in.rdbuf();    
        out.close();    
        in.close();    
        return 1; 
    } 
  }

  void EndSourceFileAction() override {
    SourceManager &SM = TheRewriter.getSourceMgr();
    llvm::errs() << "** EndSourceFileAction for: "
                 << SM.getFileEntryForID(SM.getMainFileID())->getName() << "\n";
  }

  std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI,
                                                 StringRef file) override {
    llvm::errs() << "** Creating AST consumer for: " << file << "\n";
    TheRewriter.setSourceMgr(CI.getSourceManager(), CI.getLangOpts());
    return make_unique<MyASTConsumer>(TheRewriter);
  }

private:
  Rewriter TheRewriter;
};

int main(int argc, const char **argv) {
  srand( (unsigned)time( NULL ) );
  position = atol(argv[3]);

  cout<<"-- running: moveStmt-mul"<<endl;
  cout<<"---- position: "<<position<<endl;

  llvm::Expected<clang::tooling::CommonOptionsParser> OptionsParser = CommonOptionsParser::create(argc, argv, VisitAST_Category);
  ClangTool Tool(OptionsParser->getCompilations(), OptionsParser->getSourcePathList());
  Tool.run(newFrontendActionFactory<MyFrontendAction>().get());

  return 0;
}
