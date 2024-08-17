//------------------------------------------------------------------------------
// mutate strategy: add a unuse arg in a function (not main)
// usage: addFuncArg-mul <path to main.c> -- <position>
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

static llvm::cl::OptionCategory VisitAST_Category("usage: addFuncArg-mul <path to main.c> -- <position>");
static int64_t position = 0;

static vector<string> basic_type = {"bool", "char", "unsigned char", "short", "unsigned short", "int", "unsigned int", "long", "unsigned long", "float", "double", "char*"};

// By implementing RecursiveASTVisitor, we can specify which AST nodes
// we're interested in by overriding relevant methods.
class MyASTVisitor : public RecursiveASTVisitor<MyASTVisitor> {
public:
  ASTContext *Context=NULL;
  MyASTVisitor(Rewriter &R) : TheRewriter(R) {}

  LangOptions lopt;
  string decl2str(Decl *s) {
    SourceLocation b(s->getSourceRange().getBegin()), _e(s->getSourceRange().getEnd());
    SourceLocation e(Lexer::getLocForEndOfToken(_e, 0, TheRewriter.getSourceMgr(), lopt));
    return string(TheRewriter.getSourceMgr().getCharacterData(b),
        TheRewriter.getSourceMgr().getCharacterData(e)-TheRewriter.getSourceMgr().getCharacterData(b));
  }

  bool VisitCallExpr(CallExpr *CE) {
    FunctionDecl *Callee = CE->getDirectCallee();
    if (Callee && Callee->getID() == position) {
      SourceRange callRange = CE->getSourceRange();

      Expr **args = CE->getArgs();
      unsigned numArgs = CE->getNumArgs();

      string newArg = "0";
      if(numArgs!=0)
        newArg = ", 0";

      SourceLocation call_range = callRange.getBegin();
      int insert_pos=0;
      while(TheRewriter.getSourceMgr().getCharacterData(call_range)[insert_pos]!=')'){
        insert_pos++;
      }
      SourceLocation insertionLoc = call_range.getLocWithOffset(insert_pos);
      TheRewriter.InsertText(insertionLoc, newArg);
    }

    return true;
  }

  bool VisitDecl(Decl *D) {

    if (isa<FunctionDecl>(D)){
      FunctionDecl* FunctionD=cast<FunctionDecl>(D);
      if(FunctionD->getID()==position){
        cout<<"mutate here: "<<endl;
        cout<<"func arg size: "<<FunctionD->param_size()<<endl;

        int choose_type_ind=(rand() % (basic_type.size()));
        string insert_type = basic_type[choose_type_ind];
        string new_arg = insert_type+" *FL_add_new_arg";

        SourceLocation func_range = FunctionD->getSourceRange().getBegin();
        int insert_pos=0;
        while(TheRewriter.getSourceMgr().getCharacterData(func_range)[insert_pos]!=')'){
          insert_pos++;
        }
        SourceLocation insertionLoc = func_range.getLocWithOffset(insert_pos);
        if(FunctionD->param_size()==0){
          TheRewriter.InsertText(insertionLoc,new_arg);
        }else{
          TheRewriter.InsertText(insertionLoc,","+ new_arg);
        }

      }

    }

    return true;
  }

private:
  Rewriter &TheRewriter;
};

// Implementation of the ASTConsumer interface for reading an AST produced
// by the Clang parser.
class MyASTConsumer : public ASTConsumer {
public:
  MyASTConsumer(Rewriter &R) : Visitor(R),TheRewriter(R) {}

  void HandleTranslationUnit(ASTContext &Context) override  {
    /* we can use ASTContext to get the TranslationUnitDecl, which is
       a single Decl that collectively represents the entire source file */

    Visitor.Context=&Context;
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());

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

    CopyFile("main.c", "mainori.c");
    TheRewriter.overwriteChangedFiles();
    rename("main.c", "mainvar.c");
    rename("mainori.c", "main.c");
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

  cout<<"-- running: addFuncArg-mul"<<endl;
  cout<<"---- position: "<<position<<endl;

  llvm::Expected<clang::tooling::CommonOptionsParser> OptionsParser = CommonOptionsParser::create(argc, argv, VisitAST_Category);
  ClangTool Tool(OptionsParser->getCompilations(), OptionsParser->getSourcePathList());
  Tool.run(newFrontendActionFactory<MyFrontendAction>().get());

  return 0;
}
