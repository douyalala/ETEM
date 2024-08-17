//------------------------------------------------------------------------------
// mutate strategy: add While Stmt
// check all *.c in ./testFile/ and choose all while stmt and their cond exp
// usage: addWhile-mul <path to main.c> --  <position>
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

static llvm::cl::OptionCategory VisitAST_Category("usage: addWhile-mul <path to main.c> --  <position>");
static int64_t position = -1;

// type--name
static map<string, vector<string>> can_use_decl;

static set<string> can_insert_while;
static string insert_while_stmt="while(1)";

// stage 0: get the vars can use in given position
// stage 1: check all *.c in ./testFile/ and choose all while stmt and their cond exp, rename the var
// stage 2: randomly pick a while(cond) (no need to visit AST)
// stage 3: insert while(cond) into main.c
static int stage=0;

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

  bool VisitVarDecl(VarDecl *d) {
    
    if (stage==0) {
      if(can_use_decl.count(d->getType().getAsString())==0){
        vector<string> tmp;
        can_use_decl[d->getType().getAsString()]=tmp;
      }
      can_use_decl[d->getType().getAsString()].push_back(d->getNameAsString());
    }

    return true;
  }

  bool VisitStmt(Stmt *S) {
    if(stage==0 || stage ==3){
      if(S->getID(*Context)!=position) return true;
      cout<<"mutate here"<<endl;
      if(Context==NULL){
        llvm::errs() <<"Error: Context is NULL" << "\n";
        return 0;
      }

      if(stage==3){
        TheRewriter.InsertText(S->getSourceRange().getBegin(),"while("+insert_while_stmt+")\n");
      }

      return false;
    }

    return 1;
  }

  bool VisitWhileStmt(WhileStmt *stmt) {
    Expr* while_cond = stmt->getCond();
    if(stage==1){
      cout<<"---------"<<endl;
      cout<<stmt2str(while_cond)<<endl;

      repl_vars.clear(); count=0;
      bool check_ok=extractVariablesFromExpr(while_cond);
      if(check_ok){
        cout<<"ok!"<<endl;

        SourceLocation b(while_cond->getSourceRange().getBegin());
        const char* cond_start_loc=TheRewriter.getSourceMgr().getCharacterData(b);
        string rep_cond_stmt=stmt2str(while_cond);

        // vector<pair<orivars, string>> sorted_vars;

        for(pair<orivars,string> pa: repl_vars){
          orivars ori_var=pa.first;
          string rep_var=pa.second;
          cout<<ori_var.name<<" -> "<<rep_var<<endl;
          rep_cond_stmt.replace(ori_var.start_loc-cond_start_loc,ori_var.end_loc-ori_var.start_loc,rep_var);
        }

        cout<<"-->>"<<rep_cond_stmt<<endl;
        can_insert_while.insert(rep_cond_stmt);
      }
    }
    return true;
  }

  bool extractVariablesFromExpr(Expr* E){
    if(E->getStmtClassName()=="MemberExpr") return 0;
    if (DeclRefExpr *DRE = dyn_cast<DeclRefExpr>(E)) {
      ValueDecl *VD = DRE->getDecl();
      if(!VD) return 0;
      // cout<<"-- getNameAsString: "<<VD->getNameAsString()<<endl;
      // cout<<"-- getType: "<<VD->getType().getAsString()<<endl;
      if(can_use_decl.count(VD->getType().getAsString())==0){
        return 0;
      }
      string rand_var_repl=can_use_decl[VD->getType().getAsString()][(rand() % (can_use_decl[VD->getType().getAsString()].size()))];

      orivars tmp_ori_var;
      tmp_ori_var.id=count; count++;
      tmp_ori_var.name=VD->getNameAsString();
      SourceLocation b(DRE->getSourceRange().getBegin()), _e(DRE->getSourceRange().getEnd());
      SourceLocation e(Lexer::getLocForEndOfToken(_e, 0, TheRewriter.getSourceMgr(), lopt));
      tmp_ori_var.start_loc=TheRewriter.getSourceMgr().getCharacterData(b);
      tmp_ori_var.end_loc=TheRewriter.getSourceMgr().getCharacterData(e);

      repl_vars[tmp_ori_var]=rand_var_repl;
    }

    for (Stmt *Child : E->children()) {
        if (Expr *ChildExpr = dyn_cast<Expr>(Child)) {
            bool tmp_res=extractVariablesFromExpr(ChildExpr);
            if(!tmp_res) return 0;
        }
    }

    return 1;

  }

private:
  Rewriter &TheRewriter;
  int count=0;
  class orivars{
  public:
    int id=0;
    string name;
    const char * start_loc=NULL;
    const char * end_loc=NULL;

    bool operator < (const orivars& b) const{
      return start_loc>b.start_loc;
    }
  };
  map<orivars,string> repl_vars;
};

// Implementation of the ASTConsumer interface for reading an AST produced
// by the Clang parser.
class MyASTConsumer : public ASTConsumer {
public:
  MyASTConsumer(Rewriter &R) : Visitor(R) {}

  void HandleTranslationUnit(ASTContext &Context) override  {
    /* we can use ASTContext to get the TranslationUnitDecl, which is
       a single Decl that collectively represents the entire source file */
    Visitor.Context=&Context;
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());
  }

private:
  MyASTVisitor Visitor;
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

    if(stage==3){
      CopyFile("main.c", "mainori.c");
      TheRewriter.overwriteChangedFiles();
      rename("main.c", "mainvar.c");
      rename("mainori.c", "main.c");
    }
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

  cout<<"-- running: addWhile-mul"<<endl;
  cout<<"---- position: "<<position<<endl;

  stage=0;

  llvm::Expected<clang::tooling::CommonOptionsParser> OptionsParser = CommonOptionsParser::create(argc, argv, VisitAST_Category);
  ClangTool Tool(OptionsParser->getCompilations(), OptionsParser->getSourcePathList());
  Tool.run(newFrontendActionFactory<MyFrontendAction>().get());

  stage=1;

  for(pair<string,vector<string>> pa : can_use_decl){
    cout<<pa.first<<endl;
    vector<string> vars=pa.second;
    for(string var : vars){
      cout<<var<<endl;
    }
  }

  // get all while stmt in .c files
  std::vector<std::string> sourcePaths;
  std::string srcDir = "./testFile";  // Update the correct directory path
  Twine srcDir_T(srcDir);
  std::error_code ec;
  llvm::sys::fs::directory_iterator end;
  for (llvm::sys::fs::directory_iterator iter(srcDir_T, ec); iter!=end && !ec; iter.increment(ec)) {
    if (llvm::sys::path::extension(iter->path()) == ".c") {
      sourcePaths.push_back(iter->path());
    }
  }

  llvm::Expected<clang::tooling::CommonOptionsParser> OptionsParser_1 = CommonOptionsParser::create(argc, argv, VisitAST_Category);
  ClangTool Tool_1(OptionsParser_1->getCompilations(), sourcePaths);
  Tool_1.run(newFrontendActionFactory<MyFrontendAction>().get());

  int choose_cond_ind=(rand() % (can_insert_while.size()));
  int i=0;
  cout<<"-------- can insert cond: "<<endl;
  for(string line: can_insert_while){
    if(i==choose_cond_ind){
      cout<<"choose: ";
      insert_while_stmt=line;
    }
    cout<<line<<endl;
    i++;
  }

  stage=3;
  
  llvm::Expected<clang::tooling::CommonOptionsParser> OptionsParser_3 = CommonOptionsParser::create(argc, argv, VisitAST_Category);
  ClangTool Tool_3(OptionsParser_3->getCompilations(), OptionsParser->getSourcePathList());
  Tool_3.run(newFrontendActionFactory<MyFrontendAction>().get());

  return 0;
}
