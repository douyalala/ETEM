//------------------------------------------------------------------------------
// mutate strategy: add var decl
// select positions in main.c that can mutate
// usage: addVarDecl-sel <path to main.c> --  <output dir>
// -1 means global, when mutate, add the decl to the first line of the file
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

static llvm::cl::OptionCategory VisitAST_Category("usage: addVarDecl-sel <path to main.c> --  <output dir>");
static string output_dir = "";
static ofstream out;
static vector<int64_t> res_pos;

// By implementing RecursiveASTVisitor, we can specify which AST nodes
// we're interested in by overriding relevant methods.
class MyASTVisitor : public RecursiveASTVisitor<MyASTVisitor> {
public:
  ASTContext *Context=NULL;
  MyASTVisitor(Rewriter &R) : TheRewriter(R) {}

  bool VisitStmt(Stmt *S) {
    Stmt* parent_Stmt=get_parent();
    if(parent_Stmt!=NULL){
      if(isa<CompoundStmt>(parent_Stmt)){
        TheRewriter.InsertText(S->getSourceRange().getBegin(),"// here\n"); // debug
        res_pos.push_back(S->getID(*Context));
      }
    }

    if (isa<IfStmt>(S)){
      // stmt like this:
      // if(cond)
      //   stmt;
      // the stmt after if is not CompoundStmt in AST because there are no '{' and '}'
      IfStmt* IfS= cast<IfStmt>(S);
      Stmt* thenS=IfS->getThen();
      Stmt* elseS=IfS->getElse();
      if(!isa<CompoundStmt>(thenS)){
        TheRewriter.InsertText(thenS->getSourceRange().getBegin(),"// here\n"); // debug
        res_pos.push_back(thenS->getID(*Context));
      }
      if(elseS && !isa<CompoundStmt>(elseS)){
        TheRewriter.InsertText(elseS->getSourceRange().getBegin(),"// here\n"); // debug
        res_pos.push_back(elseS->getID(*Context));
      }
    }
    else if (isa<WhileStmt>(S)){
      WhileStmt* WhileS=cast<WhileStmt>(S);
      Stmt* bodyS=WhileS->getBody();
      if(!isa<CompoundStmt>(bodyS)){
        TheRewriter.InsertText(bodyS->getSourceRange().getBegin(),"// here\n"); // debug
        res_pos.push_back(bodyS->getID(*Context));
      }
    }
    else if (isa<ForStmt>(S)){
      ForStmt* ForS=cast<ForStmt>(S);
      Stmt* bodyS=ForS->getBody();
      if(!isa<CompoundStmt>(bodyS)){
        TheRewriter.InsertText(bodyS->getSourceRange().getBegin(),"// here\n");
        res_pos.push_back(bodyS->getID(*Context));
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

    ancestor_nodes.push(S);
    result = RecursiveASTVisitor::TraverseStmt(S);
    ancestor_nodes.pop();

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

  void EndSourceFileAction() override {
    SourceManager &SM = TheRewriter.getSourceMgr();
    llvm::errs() << "** EndSourceFileAction for: "
                 << SM.getFileEntryForID(SM.getMainFileID())->getName() << "\n";

    // TheRewriter.getEditBuffer(SM.getMainFileID()).write(llvm::outs()); // debug
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
  output_dir = argv[3];

  cout<<"-- running: addVarDecl-sel"<<endl;
  cout<<"---- output_dir: "<<output_dir<<endl;

  res_pos.push_back(-1);

  llvm::Expected<clang::tooling::CommonOptionsParser> OptionsParser = CommonOptionsParser::create(argc, argv, VisitAST_Category);
  ClangTool Tool(OptionsParser->getCompilations(), OptionsParser->getSourcePathList());
  Tool.run(newFrontendActionFactory<MyFrontendAction>().get());

  out.open(output_dir,ios::trunc);
  if(out.fail()){     
    llvm::errs() <<"Error: Fail to open the out file." << "\n";
    out.close();
    return 0; 
  }
  for(long unsigned int i=0;i<res_pos.size();i++){
    out<<res_pos[i]<<endl;
  }

  return 0;
}
